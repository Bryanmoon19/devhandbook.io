---
layout: post.njk
title: "Build an MCP Server on Cloudflare Workers in 10 Minutes (No Dependencies, No Server)"
date: 2026-10-23
description: "The Model Context Protocol is the fastest-growing protocol in AI tooling, but every tutorial assumes you're building a Stripe or Notion integration. Here's a minimal, copy-paste-able MCP server running entirely on Cloudflare's free tier — zero npm dependencies, no build step, no server to babysit — that gives your AI tools base64, hashing, UUID, password, and cron utilities on tap."
tags: ["mcp", "model-context-protocol", "cloudflare-workers", "ai", "claude-code", "cursor", "openclaw", "self-hosted", "serverless", "free-tier"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-23-mcp-server-cloudflare-workers/"
affiliate: false
cta: true
---

The Model Context Protocol (MCP) is the fastest-growing thing in the AI tooling ecosystem right now. Every AI tool is adding support for it — Claude Code, Cursor, OpenClaw, and a dozen more. It's how an AI stops being a chatbot and starts being able to *do things*: read your files, query your databases, call your APIs.

But here's the problem I keep hitting: **every MCP tutorial assumes you're building a SaaS integration.** They walk you through a Stripe connector or a Notion sync. Nobody shows you the smallest possible thing — a server that just *works*, that you can deploy in ten minutes and immediately point your AI tools at.

So I built one. It's called **DevKit MCP**, it runs entirely on Cloudflare Workers' free tier, and it has **zero npm dependencies, no build step, and no server to babysit.** It's live right now at `devhandbook-mcp.bryanmoon19.workers.dev`, and the source is small enough to read in one sitting.

## What It Does

DevKit MCP exposes eight dev utilities as MCP tools:

| Tool | What it gives your AI |
|------|----------------------|
| `base64_encode` / `base64_decode` | Encode and decode base64 |
| `hash` | SHA-1 / SHA-256 / SHA-512 digests |
| `uuid` | Random UUID v4 (1–20 at a time) |
| `password` | Cryptographically secure random passwords |
| `epoch` | Unix timestamp ↔ date conversion |
| `json_format` | Pretty-print or minify JSON |
| `cron_explain` | Explain a cron expression in plain English |

These are the little things every developer reaches for a dozen times a day, but your AI can't do them reliably on its own. A model *can* do base64 in its head, but it'll occasionally hallucinate the result. Give it a tool that calls `btoa()` and it's correct 100% of the time. That's the whole point of MCP: deterministic, verifiable operations instead of model guessing.

## Why Cloudflare Workers?

Because it's the perfect fit for a stateless MCP server:

- **Free** — 100,000 requests/day on the free tier. You'll never hit that with a personal tool.
- **Global** — your AI calls a URL and it runs at the nearest Cloudflare edge, usually in single-digit milliseconds.
- **No server** — no VPS to patch, no Docker container to babysit, no `systemd` unit to write.
- **Built-in crypto** — `crypto.subtle`, `crypto.randomUUID()`, `btoa`/`atob` are all part of the Workers runtime. No dependencies needed.

## The Protocol (Simpler Than You Think)

MCP over HTTP is just JSON-RPC 2.0 sent as a `POST` to a single endpoint. Four methods is all you need:

1. `initialize` — the handshake. Server returns its name, version, and capabilities.
2. `tools/list` — returns every tool with its JSON Schema.
3. `tools/call` — runs a tool with arguments, returns the result.
4. `notifications/initialized` — a fire-and-forget notification (no response).

That's it. The whole server is a `fetch` handler that reads the JSON body, dispatches on `method`, and returns JSON. No SSE, no stdio, no long-lived connections — just stateless request/response, which is exactly what Workers is best at.

## The Code

Here's the entire server, stripped to its skeleton:

```js
export default {
  async fetch(request) {
    const { method, id, params } = await request.json();

    if (method === "initialize") {
      return json({ jsonrpc: "2.0", id, result: {
        protocolVersion: params?.protocolVersion || "2025-06-18",
        capabilities: { tools: {} },
        serverInfo: { name: "devkit-mcp", version: "1.0.0" },
      }});
    }

    if (method === "tools/list") {
      return json({ jsonrpc: "2.0", id, result: {
        tools: Object.entries(TOOLS).map(([name, t]) => ({
          name, description: t.description, inputSchema: t.inputSchema,
        })),
      }});
    }

    if (method === "tools/call") {
      const { name, arguments: args = {} } = params;
      const tool = TOOLS[name];
      const result = await tool.handler(args);
      return json({ jsonrpc: "2.0", id, result });
    }

    return json({ jsonrpc: "2.0", id, error: { code: -32601, message: "Method not found" } });
  },
};
```

Each tool is just an entry in a `TOOLS` object — a description, a JSON Schema, and a handler function:

```js
const TOOLS = {
  hash: {
    description: "Compute SHA-256 digest of a string.",
    inputSchema: {
      type: "object",
      properties: { text: { type: "string" } },
      required: ["text"],
    },
    handler: async ({ text }) => {
      const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
      return { content: [{ type: "text",
        text: [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("") }] };
    },
  },
};
```

Add a tool and `tools/list` + `tools/call` pick it up automatically. No wiring, no registration.

## Deploy It Yourself

```bash
git clone https://github.com/Bryanmoon19/devhandbook-mcp.git
cd devhandbook-mcp
export CLOUDFLARE_API_TOKEN="your-token"
npm install
npm run deploy
```

You'll get a `*.workers.dev` URL back in seconds. **That URL is your MCP endpoint.**

## Connect Your AI

Point any MCP client at the URL. For Claude Code:

```bash
claude mcp add devkit --transport http https://devhandbook-mcp.bryanmoon19.workers.dev
```

Then ask it to "generate a 24-character password" or "what's the SHA-256 of 'hello'?" and it'll call the tool instead of guessing.

## Test It With curl

You can verify the whole thing without any AI tool:

```bash
# Handshake
curl -X POST https://devhandbook-mcp.bryanmoon19.workers.dev \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}'

# List tools
curl -X POST https://devhandbook-mcp.bryanmoon19.workers.dev \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

# Call a tool
curl -X POST https://devhandbook-mcp.bryanmoon19.workers.dev \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"password","arguments":{"length":24}}}'
```

## The Bigger Picture

This is the same idea as [MCP for homelabs](/blog/2026-07-21-mcp-for-homelab-build-first-server/) — take the protocol and apply it to a *real, concrete, tiny* problem instead of another SaaS integration. Once you've seen how small a working MCP server can be, the "universal USB port for AI" framing finally makes sense.

And because it runs on the same Cloudflare Workers stack as the rest of devhandbook.io, there's nothing new to learn. If you've deployed a Worker before, you can build an MCP server. The protocol is the easy part — the hard part is deciding *what* to expose.

The full source is up at [github.com/Bryanmoon19/devhandbook-mcp](https://github.com/Bryanmoon19/devhandbook-mcp). Fork it, drop in your own tools, and give your AI something it can actually *do*.
