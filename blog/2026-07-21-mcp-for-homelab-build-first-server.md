---
layout: post.njk
title: "MCP for Homelab: Build Your First Self-Hosted MCP Server"
date: 2026-07-21
description: "Connect Claude Code, OpenClaw, and your AI tools directly to Proxmox, Docker, and Home Assistant with the Model Context Protocol. Hands-on guide with working code."
tags: ["ai", "mcp", "self-hosting", "homelab", "claude-code", "proxmox", "docker", "home-assistant", "automation"]
---

The Model Context Protocol (MCP) is the fastest-growing protocol in the AI ecosystem right now. `open-connector` hit nearly 3,000 GitHub stars in 30 days. `mcpsnoop` — literally "Wireshark for MCP" — is at 275 stars. Every AI tool is adding MCP support.

But here's the thing: **every MCP tutorial is written for SaaS developers.** They assume you're building a Stripe integration or a Notion connector. Nobody is writing about what MCP means for the homelab.

So let's fix that. By the end of this post, you'll have a working MCP server that lets Claude Code or OpenClaw control your Proxmox containers, restart Docker services, and query Home Assistant — all from natural language.

## What Is MCP, Actually?

MCP is a protocol that lets AI tools talk to external services. Think of it as a universal USB port for AI. Instead of every AI tool building its own integration for every service, MCP defines a standard way for tools to discover and use capabilities.

The architecture is simple:

```
AI Tool (Claude Code, OpenClaw, etc.)
    │
    ▼
MCP Client (built into the AI tool)
    │
    ▼  (stdio or HTTP)
MCP Server (your code)
    │
    ▼
Your Homelab (Proxmox, Docker, HA, etc.)
```

An MCP server exposes **tools** (actions the AI can take), **resources** (data the AI can read), and **prompts** (templates for common tasks). The AI tool discovers these automatically — no manual configuration per service.

## Why This Matters for Homelabbers

Right now, if you want Claude Code to restart a Docker container, you have to give it shell access. Full shell access. That's terrifying.

With MCP, you expose exactly what you want:

- ✅ "Restart the Plex container" — allowed
- ✅ "List all running containers" — allowed
- ❌ `rm -rf /` — not even possible, because the MCP server only exposes the tools you define

This is the difference between giving your AI a key to your house vs. giving it a specific list of things it's allowed to touch.

## What We're Building

A Python MCP server called `homelab-mcp` that exposes:

| Tool | What It Does |
|------|-------------|
| `list_containers` | List all Proxmox containers with status |
| `container_action` | Start/stop/restart a Proxmox container |
| `list_docker` | List Docker containers on a remote host |
| `docker_action` | Start/stop/restart a Docker container |
| `ha_entities` | Query Home Assistant entity states |
| `ha_service` | Call a Home Assistant service |

By the end, you'll be able to type `restart the Plex container` in Claude Code and it'll just work.

## Prerequisites

- Python 3.10+ (your homelab probably has this)
- A Proxmox host (we'll use the API)
- Docker running somewhere (local or remote)
- Home Assistant (optional, for the HA tools)
- Claude Code, OpenClaw, or any MCP-compatible client

## Step 1: Project Setup

```bash
mkdir ~/homelab-mcp && cd ~/homelab-mcp
python3 -m venv venv
source venv/bin/activate
pip install mcp proxmoxer docker requests
```

Create `server.py`:

```python
#!/usr/bin/env python3
"""Homelab MCP Server — Expose Proxmox, Docker, and Home Assistant to AI tools."""

import os
import json
import asyncio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import proxmoxer
import docker
import requests

# ── Configuration (use env vars in production) ──────────────────────

PROXMOX_HOST = os.getenv("PROXMOX_HOST", "192.168.7.134")
PROXMOX_USER = os.getenv("PROXMOX_USER", "root@pam")
PROXMOX_TOKEN = os.getenv("PROXMOX_TOKEN", "")
PROXMOX_TOKEN_NAME = os.getenv("PROXMOX_TOKEN_NAME", "moonbot")

DOCKER_HOST = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
# For remote Docker: "ssh://root@192.168.7.202"

HA_URL = os.getenv("HA_URL", "http://192.168.7.46:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")

# ── Proxmox Helpers ─────────────────────────────────────────────────

def get_proxmox():
    return proxmoxer.ProxmoxAPI(
        PROXMOX_HOST,
        user=PROXMOX_USER,
        token_name=PROXMOX_TOKEN_NAME,
        token_value=PROXMOX_TOKEN,
        verify_ssl=False,
    )

def list_proxmox_containers():
    """Return all LXC containers with their status."""
    prox = get_proxmox()
    nodes = prox.nodes.get()
    results = []
    for node in nodes:
        node_name = node["node"]
        containers = prox.nodes(node_name).lxc.get()
        for ct in containers:
            results.append({
                "node": node_name,
                "vmid": ct["vmid"],
                "name": ct.get("name", "unknown"),
                "status": ct["status"],
                "cpu": ct.get("cpu", 0),
                "mem": ct.get("mem", 0),
                "uptime": ct.get("uptime", 0),
            })
    return results

def proxmox_container_action(vmid: int, action: str, node: str = None):
    """Start, stop, or restart a Proxmox container."""
    prox = get_proxmox()
    if not node:
        # Find the node
        for n in prox.nodes.get():
            try:
                prox.nodes(n["node"]).lxc(vmid).status.current.get()
                node = n["node"]
                break
            except Exception:
                continue
    if not node:
        return {"error": f"Container {vmid} not found on any node"}

    if action == "start":
        prox.nodes(node).lxc(vmid).status.start.post()
    elif action == "stop":
        prox.nodes(node).lxc(vmid).status.stop.post()
    elif action == "restart":
        prox.nodes(node).lxc(vmid).status.reboot.post()
    else:
        return {"error": f"Unknown action: {action}"}

    return {"success": True, "vmid": vmid, "action": action, "node": node}

# ── Docker Helpers ───────────────────────────────────────────────────

def get_docker():
    return docker.DockerClient(base_url=DOCKER_HOST)

def list_docker_containers():
    """List all Docker containers with status."""
    client = get_docker()
    containers = client.containers.list(all=True)
    return [
        {
            "id": c.short_id,
            "name": c.name,
            "status": c.status,
            "image": c.image.tags[0] if c.image.tags else "unknown",
        }
        for c in containers
    ]

def docker_container_action(name: str, action: str):
    """Start, stop, or restart a Docker container by name."""
    client = get_docker()
    try:
        container = client.containers.get(name)
    except docker.errors.NotFound:
        return {"error": f"Container '{name}' not found"}

    if action == "start":
        container.start()
    elif action == "stop":
        container.stop()
    elif action == "restart":
        container.restart()
    else:
        return {"error": f"Unknown action: {action}"}

    return {"success": True, "name": name, "action": action}

# ── Home Assistant Helpers ────────────────────────────────────────────

def ha_request(endpoint: str, method: str = "GET", data: dict = None):
    """Make an authenticated request to Home Assistant."""
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"{HA_URL}/api/{endpoint}"
    if method == "GET":
        resp = requests.get(url, headers=headers, timeout=10)
    elif method == "POST":
        resp = requests.post(url, headers=headers, json=data, timeout=10)
    else:
        return {"error": f"Unsupported method: {method}"}
    resp.raise_for_status()
    return resp.json()

def ha_get_entities(filter_domain: str = None):
    """Get Home Assistant entity states, optionally filtered by domain."""
    states = ha_request("states")
    results = []
    for s in states:
        domain = s["entity_id"].split(".")[0]
        if filter_domain and domain != filter_domain:
            continue
        results.append({
            "entity_id": s["entity_id"],
            "state": s["state"],
            "friendly_name": s["attributes"].get("friendly_name", ""),
        })
    return results

def ha_call_service(domain: str, service: str, entity_id: str = None, data: dict = None):
    """Call a Home Assistant service."""
    payload = {}
    if entity_id:
        payload["entity_id"] = entity_id
    if data:
        payload.update(data)
    return ha_request(f"services/{domain}/{service}", method="POST", data=payload)

# ── MCP Server ───────────────────────────────────────────────────────

server = Server("homelab-mcp")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_containers",
            description="List all Proxmox LXC containers with their status, CPU, and memory usage",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="container_action",
            description="Start, stop, or restart a Proxmox LXC container by VMID",
            inputSchema={
                "type": "object",
                "properties": {
                    "vmid": {"type": "integer", "description": "Container VMID"},
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "restart"],
                        "description": "Action to perform",
                    },
                },
                "required": ["vmid", "action"],
            },
        ),
        Tool(
            name="list_docker",
            description="List all Docker containers with their status",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="docker_action",
            description="Start, stop, or restart a Docker container by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Container name"},
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "restart"],
                        "description": "Action to perform",
                    },
                },
                "required": ["name", "action"],
            },
        ),
        Tool(
            name="ha_entities",
            description="Query Home Assistant entity states, optionally filtered by domain (light, switch, sensor, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_domain": {
                        "type": "string",
                        "description": "Optional: filter by domain (e.g., 'light', 'switch', 'sensor')",
                    },
                },
            },
        ),
        Tool(
            name="ha_service",
            description="Call a Home Assistant service (e.g., turn on a light, run an automation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string", "description": "Service domain (e.g., 'light', 'switch', 'automation')"},
                    "service": {"type": "string", "description": "Service name (e.g., 'turn_on', 'turn_off', 'trigger')"},
                    "entity_id": {"type": "string", "description": "Target entity ID"},
                    "data": {"type": "object", "description": "Additional service data"},
                },
                "required": ["domain", "service"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "list_containers":
            result = list_proxmox_containers()
        elif name == "container_action":
            result = proxmox_container_action(
                vmid=arguments["vmid"],
                action=arguments["action"],
            )
        elif name == "list_docker":
            result = list_docker_containers()
        elif name == "docker_action":
            result = docker_container_action(
                name=arguments["name"],
                action=arguments["action"],
            )
        elif name == "ha_entities":
            result = ha_get_entities(
                filter_domain=arguments.get("filter_domain"),
            )
        elif name == "ha_service":
            result = ha_call_service(
                domain=arguments["domain"],
                service=arguments["service"],
                entity_id=arguments.get("entity_id"),
                data=arguments.get("data"),
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationCapabilities(
                sampling={},
                experimental={},
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 2: Configure Environment

Create a `.env` file (add to `.gitignore` immediately):

```bash
# Proxmox API
PROXMOX_HOST=192.168.7.134
PROXMOX_USER=root@pam
PROXMOX_TOKEN_NAME=moonbot
PROXMOX_TOKEN=your-proxmox-api-token-here

# Docker (local socket or remote SSH)
DOCKER_HOST=unix:///var/run/docker.sock
# DOCKER_HOST=ssh://root@192.168.7.202  # Remote Docker

# Home Assistant
HA_URL=http://192.168.7.46:8123
HA_TOKEN=your-long-lived-access-token-here
```

**Getting a Proxmox API token:**
1. Proxmox web UI → Datacenter → Permissions → API Tokens
2. Add token for `root@pam!moonbot` (uncheck "Privilege Separation" for full access)
3. Copy the secret — you only see it once

**Getting a Home Assistant token:**
1. HA → your profile (bottom left) → Security → Long-Lived Access Tokens
2. Create token, copy it immediately

## Step 3: Test It Locally

```bash
source venv/bin/activate
source .env  # or: export $(cat .env | xargs)
python3 server.py
```

The server starts and waits for MCP client connections over stdio. You can test it with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python3 server.py
```

This opens a web UI where you can call each tool and see the responses.

## Step 4: Connect to Claude Code

Claude Code supports MCP servers natively. Add to your Claude Code config:

```json
// ~/.claude/settings.json
{
  "mcpServers": {
    "homelab": {
      "command": "python3",
      "args": ["/Users/bryan/homelab-mcp/server.py"],
      "env": {
        "PROXMOX_HOST": "192.168.7.134",
        "PROXMOX_TOKEN": "your-token-here",
        "DOCKER_HOST": "ssh://root@192.168.7.202",
        "HA_URL": "http://192.168.7.46:8123",
        "HA_TOKEN": "your-ha-token-here"
      }
    }
  }
}
```

Restart Claude Code. Now you can type:

> "What containers are running on Proxmox right now?"

> "Restart the Plex container"

> "Turn off all the lights in the living room"

> "Is the TeslaMate container healthy?"

Claude Code discovers the tools automatically and uses them.

## Step 5: Connect to OpenClaw

OpenClaw supports MCP servers through its plugin system. Add to your OpenClaw config:

```json
{
  "mcp": {
    "servers": {
      "homelab": {
        "command": "python3",
        "args": ["/Users/bryan/homelab-mcp/server.py"],
        "env": {
          "PROXMOX_HOST": "192.168.7.134",
          "PROXMOX_TOKEN": "your-token-here"
        }
      }
    }
  }
}
```

Restart OpenClaw. Your Telegram bot can now control your homelab.

## Going Further: What Else Can You Expose?

The pattern is the same for anything with an API:

| Service | What to Expose | API |
|---------|---------------|-----|
| **Pi-hole** | Enable/disable blocking, query stats | `http://pi.hole/admin/api.php` |
| **Plex** | List recently added, check server health | `https://plex.tv/api/v2` |
| **TeslaMate** | Battery level, location, charging status | MQTT or REST API |
| **UniFi** | List clients, restart APs | UniFi Controller API |
| **Uptime Kuma** | Monitor status, add monitors | REST API |
| **Sonarr/Radarr** | Queue status, add releases | *arr API |
| **Tailscale** | List devices, check connectivity | Local API |

Each one is just another set of tools in your MCP server. The AI tool discovers them all automatically.

## Security: The Right Way

MCP is powerful, which means you need to be careful. Here's the security checklist:

### 1. Never Expose Raw Shell Access

Don't write a tool that runs arbitrary commands. That defeats the purpose. Expose specific, named actions.

```python
# ❌ BAD: Arbitrary command execution
def run_command(cmd: str):
    return subprocess.check_output(cmd, shell=True)

# ✅ GOOD: Specific, named actions
def restart_container(name: str):
    # Only restart, nothing else
    client.containers.get(name).restart()
```

### 2. Use Read-Only Where Possible

Not every tool needs write access. A `list_containers` tool is read-only and safe. A `container_action` tool with `start/stop/restart` is more dangerous — consider whether you actually need it.

### 3. Run in an Isolated Environment

Run your MCP server in a dedicated LXC container or Docker container with minimal permissions. If something goes wrong, the blast radius is contained.

```bash
# Create a minimal LXC for the MCP server
pct create 200 \
  local:vztmpl/ubuntu-24.04-standard_24.04-1_amd64.tar.zst \
  --hostname mcp-server \
  --memory 512 \
  --cores 1 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp
```

### 4. Audit Everything

Log every tool call. You want to know what your AI is doing:

```python
import logging
logging.basicConfig(
    filename="/var/log/homelab-mcp.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    logging.info(f"Tool called: {name} with args: {arguments}")
    # ... rest of handler
```

### 5. Use Environment Variables for Secrets

Never hardcode tokens. Use `.env` files or systemd `EnvironmentFile`. The MCP config in Claude Code/OpenClaw supports `env` for this reason.

## Real-World Example: "Why Is Plex Down?"

Here's what happens when you ask Claude Code "Why is Plex down?" with this MCP server connected:

1. Claude calls `list_docker` → sees `plex` container is `exited`
2. Claude calls `docker_action(name="plex", action="start")` → container starts
3. Claude calls `list_docker` again → confirms `plex` is `running`
4. Claude reports: "Plex was stopped. I've restarted it — it should be back up now."

No SSH. No manual commands. No context-switching. Just natural language.

## The Bigger Picture

MCP is going to be everywhere by the end of 2026. Anthropic is pushing it hard. OpenAI has their own version. OpenClaw supports it. Every major AI tool will.

The homelabbers who build MCP servers now are going to have AI assistants that actually understand and control their infrastructure. Everyone else will be copy-pasting commands from ChatGPT.

This is the moment to get ahead of it.

## What's Next

- **More services:** Add Pi-hole, UniFi, TeslaMate tools to your server
- **Prompts:** Define common workflows as MCP prompts (e.g., "health check" that runs through all services)
- **Resources:** Expose dashboards, logs, and metrics as MCP resources the AI can read
- **Share it:** Package your MCP server and share it with the homelab community

The code in this post is a starting point. Fork it, extend it, make it yours. The MCP ecosystem is young and the homelab corner of it is completely empty. Be the first.

---

*Got an MCP server running in your homelab? I'd love to hear about it. What services are you exposing? What's the coolest thing your AI assistant can do now?*
