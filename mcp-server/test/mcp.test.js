import { test } from "node:test";
import assert from "node:assert";

// Import the module logic by spawning the server via stdio is heavy;
// instead we unit-test the pure helpers by importing index.js functions is not possible
// (they're not exported). We test end-to-end via stdio JSON-RPC instead.

import { spawn } from "node:child_process";

function rpcRequest(messages) {
  return new Promise((resolve, reject) => {
    const child = spawn("node", ["index.js"], { cwd: new URL("..", import.meta.url).pathname });
    let buf = "";
    child.stdout.on("data", (d) => (buf += d.toString()));
    child.stderr.on("data", () => {}); // ignore
    child.on("error", reject);
    child.on("close", () => {
      // Parse newline-delimited JSON-RPC responses
      const lines = buf.split("\n").filter((l) => l.trim());
      resolve(lines.map((l) => JSON.parse(l)));
    });
    for (const m of messages) {
      child.stdin.write(JSON.stringify(m) + "\n");
    }
    child.stdin.end();
  });
}

test("tools/list returns 5 tools", async () => {
  const responses = await rpcRequest([
    { jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "test", version: "1.0.0" } } },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} },
  ]);
  const list = responses.find((r) => r.id === 2);
  assert.ok(list, "tools/list response present");
  const tools = list.result.tools;
  assert.equal(tools.length, 5);
  const names = tools.map((t) => t.name).sort();
  assert.deepEqual(names, ["base64", "json_format", "jwt_decode", "password_gen", "timestamp"]);
});

test("jwt_decode decodes a token", async () => {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString("base64url");
  const payload = Buffer.from(JSON.stringify({ sub: "123", exp: 9999999999 })).toString("base64url");
  const token = `${header}.${payload}.sig`;
  const responses = await rpcRequest([
    { jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "t", version: "1" } } },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    { jsonrpc: "2.0", id: 2, method: "tools/call", params: { name: "jwt_decode", arguments: { token } } },
  ]);
  const call = responses.find((r) => r.id === 2);
  assert.ok(call.result);
  const text = call.result.content[0].text;
  const parsed = JSON.parse(text);
  assert.equal(parsed.header.alg, "HS256");
  assert.equal(parsed.payload.sub, "123");
  assert.equal(parsed.expiry.expired, false); // exp in year 2286 — not expired
});

test("base64 encode/decode roundtrip", async () => {
  const responses = await rpcRequest([
    { jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "t", version: "1" } } },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    { jsonrpc: "2.0", id: 2, method: "tools/call", params: { name: "base64", arguments: { action: "encode", input: "hello world" } } },
    { jsonrpc: "2.0", id: 3, method: "tools/call", params: { name: "base64", arguments: { action: "decode", input: "aGVsbG8gd29ybGQ=" } } },
  ]);
  const enc = responses.find((r) => r.id === 2);
  const dec = responses.find((r) => r.id === 3);
  assert.equal(enc.result.content[0].text, "aGVsbG8gd29ybGQ=");
  assert.equal(dec.result.content[0].text, "hello world");
});

test("json_format validates and formats", async () => {
  const responses = await rpcRequest([
    { jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "t", version: "1" } } },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    { jsonrpc: "2.0", id: 2, method: "tools/call", params: { name: "json_format", arguments: { input: `{"a":1,"b":[2,3]}`, mode: "format", indent: 2 } } },
    { jsonrpc: "2.0", id: 3, method: "tools/call", params: { name: "json_format", arguments: { input: `{"broken":`, mode: "validate" } } },
  ]);
  const fmt = responses.find((r) => r.id === 2);
  const val = responses.find((r) => r.id === 3);
  assert.ok(fmt.result.content[0].text.includes('"a": 1'));
  assert.equal(JSON.parse(val.result.content[0].text).valid, false);
});

test("timestamp converts both directions", async () => {
  const responses = await rpcRequest([
    { jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "t", version: "1" } } },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    { jsonrpc: "2.0", id: 2, method: "tools/call", params: { name: "timestamp", arguments: { convert: "toDate", value: "1700000000", unit: "seconds" } } },
    { jsonrpc: "2.0", id: 3, method: "tools/call", params: { name: "timestamp", arguments: { convert: "toTimestamp", value: "2023-11-14T22:13:20.000Z" } } },
  ]);
  const toDate = responses.find((r) => r.id === 2);
  const toTs = responses.find((r) => r.id === 3);
  const d = JSON.parse(toDate.result.content[0].text);
  assert.equal(d.unixSeconds, 1700000000);
  assert.equal(d.iso, "2023-11-14T22:13:20.000Z");
  const t = JSON.parse(toTs.result.content[0].text);
  assert.equal(t.unixSeconds, 1700000000);
});

test("password_gen respects length and count", async () => {
  const responses = await rpcRequest([
    { jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "t", version: "1" } } },
    { jsonrpc: "2.0", method: "notifications/initialized" },
    { jsonrpc: "2.0", id: 2, method: "tools/call", params: { name: "password_gen", arguments: { length: 20, count: 3, symbols: false } } },
  ]);
  const call = responses.find((r) => r.id === 2);
  const out = call.result.content[0].text;
  const arr = JSON.parse(out);
  assert.equal(arr.length, 3);
  for (const pw of arr) {
    assert.equal(pw.length, 20);
    assert.match(pw, /[A-Z]/);
    assert.match(pw, /[a-z]/);
    assert.match(pw, /[0-9]/);
  }
});
