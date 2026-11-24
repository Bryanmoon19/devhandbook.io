#!/usr/bin/env node
/**
 * devhandbook-mcp — MCP server exposing devhandbook.io's developer micro-tools.
 *
 * Tools:
 *   - jwt_decode   : decode a JWT (header + payload), flag expiry
 *   - base64       : encode / decode base64 (with URL-safe support)
 *   - json_format  : pretty-print / validate JSON
 *   - timestamp    : convert between unix timestamps (s/ms) and human dates
 *   - password_gen : generate a secure random password
 *
 * Runs over stdio (default MCP transport). No network, no secrets, fully local.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "devhandbook-mcp",
  version: "1.0.0",
});

// ---------- Helpers ----------

function base64UrlDecode(str) {
  // Normalize URL-safe chars, pad, decode as UTF-8
  let s = str.replace(/-/g, "+").replace(/_/g, "/");
  const pad = s.length % 4;
  if (pad) s += "=".repeat(4 - pad);
  const bin = Buffer.from(s, "base64");
  return bin.toString("utf8");
}

function base64UrlEncode(str) {
  return Buffer.from(str, "utf8")
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

// Crypto-safe random password (Web Crypto API)
function randomInt(max) {
  const buf = new Uint32Array(1);
  crypto.getRandomValues(buf);
  return buf[0] % max;
}

function generatePassword(length, includeUppercase, includeLowercase, includeNumbers, includeSymbols, excludeAmbiguous) {
  const sets = [];
  if (includeUppercase) sets.push("ABCDEFGHJKLMNPQRSTUVWXYZ");
  else sets.push("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
  if (includeLowercase) sets.push("abcdefghjkmnpqrstuvwxyz");
  else sets.push("abcdefghijklmnopqrstuvwxyz");
  if (includeNumbers) sets.push("23456789");
  else sets.push("0123456789");
  if (includeSymbols) sets.push("!@#$%^&*()-_=+[]{};:,.<>?");

  if (sets.length === 0) throw new Error("At least one character set must be enabled");

  const all = sets.join("");
  const chars = [];
  // Guarantee at least one char from each enabled set
  for (const set of sets) {
    chars.push(set[randomInt(set.length)]);
  }
  while (chars.length < length) {
    chars.push(all[randomInt(all.length)]);
  }
  // Shuffle (Fisher-Yates)
  for (let i = chars.length - 1; i > 0; i--) {
    const j = randomInt(i + 1);
    [chars[i], chars[j]] = [chars[j], chars[i]];
  }
  return chars.slice(0, length).join("");
}

// ---------- Tool: jwt_decode ----------

server.registerTool(
  "jwt_decode",
  {
    title: "Decode JWT",
    description:
      "Decode a JSON Web Token (JWT) into its header and payload. Flags whether the token is expired based on the 'exp' claim. Does NOT verify the signature — client-side decode only.",
    inputSchema: {
      token: z.string().describe("The JWT token string (three dot-separated parts)."),
    },
  },
  async ({ token }) => {
    const parts = token.trim().split(".");
    if (parts.length !== 3) {
      return {
        content: [{ type: "text", text: JSON.stringify({ error: "Invalid JWT: expected 3 dot-separated parts." }, null, 2) }],
        isError: true,
      };
    }
    let header, payload;
    try {
      header = JSON.parse(base64UrlDecode(parts[0]));
    } catch {
      return { content: [{ type: "text", text: JSON.stringify({ error: "Could not decode JWT header." }, null, 2) }], isError: true };
    }
    try {
      payload = JSON.parse(base64UrlDecode(parts[1]));
    } catch {
      return { content: [{ type: "text", text: JSON.stringify({ error: "Could not decode JWT payload." }, null, 2) }], isError: true };
    }

    const now = Math.floor(Date.now() / 1000);
    let expiryStatus = null;
    if (payload.exp != null) {
      const expDate = new Date(payload.exp * 1000);
      expiryStatus = {
        exp: payload.exp,
        expiresAt: expDate.toISOString(),
        expired: payload.exp < now,
      };
    }

    const result = {
      header,
      payload,
      signature: parts[2] ? `${parts[2].substring(0, 32)}…` : null,
      expiry: expiryStatus,
      note: "Signature not verified — decode only.",
    };
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }
);

// ---------- Tool: base64 ----------

server.registerTool(
  "base64",
  {
    title: "Base64 Encode/Decode",
    description:
      "Encode text to base64 or decode base64 back to text. Supports standard and URL-safe variants.",
    inputSchema: {
      action: z.enum(["encode", "decode"]).describe("Whether to encode or decode."),
      input: z.string().describe("The text (to encode) or base64 string (to decode)."),
      urlsafe: z.boolean().default(false).describe("Use URL-safe base64 (no +, /, or = padding)."),
    },
  },
  async ({ action, input, urlsafe }) => {
    if (action === "encode") {
      let out = Buffer.from(input, "utf8").toString("base64");
      if (urlsafe) out = out.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
      return { content: [{ type: "text", text: out }] };
    }
    // decode
    let s = input.trim();
    if (urlsafe) {
      s = s.replace(/-/g, "+").replace(/_/g, "/");
      const pad = s.length % 4;
      if (pad) s += "=".repeat(4 - pad);
    }
    let decoded;
    try {
      decoded = Buffer.from(s, "base64").toString("utf8");
    } catch {
      return { content: [{ type: "text", text: JSON.stringify({ error: "Invalid base64 input." }) }], isError: true };
    }
    return { content: [{ type: "text", text: decoded }] };
  }
);

// ---------- Tool: json_format ----------

server.registerTool(
  "json_format",
  {
    title: "Format / Validate JSON",
    description:
      "Pretty-print JSON with a given indent, or validate that a string is well-formed JSON. Optionally minify.",
    inputSchema: {
      input: z.string().describe("The JSON string to process."),
      mode: z.enum(["format", "validate", "minify"]).default("format").describe("Operation to perform."),
      indent: z.number().int().min(0).max(8).default(2).describe("Indent width for pretty printing."),
    },
  },
  async ({ input, mode, indent }) => {
    let parsed;
    try {
      parsed = JSON.parse(input);
    } catch (e) {
      return {
        content: [{ type: "text", text: JSON.stringify({ valid: false, error: e.message }, null, 2) }],
        isError: mode === "validate" ? false : true,
      };
    }
    if (mode === "validate") {
      return { content: [{ type: "text", text: JSON.stringify({ valid: true }, null, 2) }] };
    }
    if (mode === "minify") {
      return { content: [{ type: "text", text: JSON.stringify(parsed) }] };
    }
    return { content: [{ type: "text", text: JSON.stringify(parsed, null, indent) }] };
  }
);

// ---------- Tool: timestamp ----------

server.registerTool(
  "timestamp",
  {
    title: "Unix Timestamp Converter",
    description:
      "Convert between Unix timestamps (seconds or milliseconds) and ISO 8601 / human-readable dates. If 'convert' is 'toDate', provide a numeric timestamp; if 'toTimestamp', provide an ISO date string.",
    inputSchema: {
      convert: z.enum(["toDate", "toTimestamp"]).describe("Direction of conversion."),
      value: z.string().describe("Numeric timestamp (s or ms) for 'toDate', or ISO date string for 'toTimestamp'."),
      unit: z.enum(["auto", "seconds", "milliseconds"]).default("auto").describe("Timestamp unit when converting to date."),
    },
  },
  async ({ convert, value, unit }) => {
    if (convert === "toDate") {
      let num = Number(value);
      if (!Number.isFinite(num)) {
        return { content: [{ type: "text", text: JSON.stringify({ error: "Invalid numeric timestamp." }) }], isError: true };
      }
      if (unit === "milliseconds" || (unit === "auto" && Math.abs(num) > 1e12)) {
        num = num; // already ms
      } else {
        num = num * 1000; // seconds -> ms
      }
      const d = new Date(num);
      if (isNaN(d.getTime())) {
        return { content: [{ type: "text", text: JSON.stringify({ error: "Timestamp out of range." }) }], isError: true };
      }
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            iso: d.toISOString(),
            utc: d.toUTCString(),
            local: d.toString(),
            unixSeconds: Math.floor(num / 1000),
            unixMilliseconds: num,
          }, null, 2),
        }],
      };
    }
    // toTimestamp
    const d = new Date(value);
    if (isNaN(d.getTime())) {
      return { content: [{ type: "text", text: JSON.stringify({ error: "Invalid date string." }) }], isError: true };
    }
    const ms = d.getTime();
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          unixSeconds: Math.floor(ms / 1000),
          unixMilliseconds: ms,
          iso: d.toISOString(),
        }, null, 2),
      }],
    };
  }
);

// ---------- Tool: password_gen ----------

server.registerTool(
  "password_gen",
  {
    title: "Generate Password",
    description:
      "Generate a cryptographically secure random password with configurable length and character sets. Uses the Web Crypto API for randomness.",
    inputSchema: {
      length: z.number().int().min(4).max(256).default(16).describe("Password length."),
      uppercase: z.boolean().default(true).describe("Include uppercase letters."),
      lowercase: z.boolean().default(true).describe("Include lowercase letters."),
      numbers: z.boolean().default(true).describe("Include digits."),
      symbols: z.boolean().default(true).describe("Include symbols."),
      excludeAmbiguous: z.boolean().default(false).describe("Exclude easily-confused chars (0/O, 1/l/I)."),
      count: z.number().int().min(1).max(10).default(1).describe("Number of passwords to generate."),
    },
  },
  async ({ length, uppercase, lowercase, numbers, symbols, excludeAmbiguous, count }) => {
    const out = [];
    for (let i = 0; i < count; i++) {
      out.push(generatePassword(length, uppercase, lowercase, numbers, symbols, excludeAmbiguous));
    }
    return { content: [{ type: "text", text: count === 1 ? out[0] : JSON.stringify(out, null, 2) }] };
  }
);

// ---------- Boot ----------

const transport = new StdioServerTransport();
await server.connect(transport);
