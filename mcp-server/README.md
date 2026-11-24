# devhandbook-mcp

An [MCP](https://modelcontextprotocol.io) (Model Context Protocol) server that exposes
[devhandbook.io](https://devhandbook.io)'s free developer micro-tools to AI agents
(Claude, Cursor, and any MCP client).

No new product — just packaging the tools you already use in the browser into the
dominant AI-agent integration layer.

## Tools

| Tool          | What it does                                                            |
| ------------- | ----------------------------------------------------------------------- |
| `jwt_decode`  | Decode a JWT into header + payload, flag expiry (signature NOT verified) |
| `base64`      | Encode/decode base64, standard or URL-safe                                |
| `json_format` | Pretty-print, validate, or minify JSON                                    |
| `timestamp`   | Convert between Unix timestamps (s/ms) and ISO/human dates                |
| `password_gen`| Cryptographically secure random password generator (Web Crypto API)       |

## Why

devhandbook.io already ships ~40 free, 100%-client-side developer tools. Developers
spend more and more time inside AI agents (Claude Code, Cursor, etc.). This server
lets an agent do a JWT decode, base64 round-trip, JSON format, or password generation
in-context without leaving the editor — and puts devhandbook.io's name in the tool list.

## Install & run

```bash
cd mcp-server
npm install
node index.js          # starts the stdio MCP server
```

## Connect to Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "devhandbook": {
      "command": "node",
      "args": ["/path/to/devhandbook.io/mcp-server/index.js"]
    }
  }
}
```

## Connect to Claude Code / Cursor

```bash
# Claude Code
claude mcp add devhandbook -- node /path/to/devhandbook.io/mcp-server/index.js

# Cursor — add to ~/.cursor/mcp.json
```

## Test

```bash
npm test
```

---

**License:** MIT
