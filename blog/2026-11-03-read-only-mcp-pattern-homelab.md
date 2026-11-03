---
layout: post.njk
title: "The Read-Only MCP Pattern: Give Your AI Eyes on Your Homelab (Without Handing It the Keys)"
date: 2026-11-03
description: "Last time I told you MCP servers are your new attack surface. Here's the pattern that makes them safe enough to actually use: a read-only MCP server whose every tool is an HTTP health probe, no tokens, no writes, no SSH — the worst it can do is tell you a service is down."
tags: ["mcp", "model-context-protocol", "self-hosted", "homelab", "security", "read-only", "ai", "claude-code", "cursor", "automation"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-03-read-only-mcp-pattern-homelab/"
affiliate: false
cta: true
---

Three months ago I wrote a post that I still get emails about: [MCP Servers Are Your New Attack Surface](/blog/2026-08-16-mcp-servers-attack-surface). The thesis was blunt — there are 21,000+ MCP servers exposed to the internet, and "no MCP output is safe" has gone from a hot take to a research consensus. The protocol grew faster than the security thinking around it, and the honeymoon was over.

I still stand by every word of that post. But it left a question dangling that I've been circling since: **if MCP is this dangerous, how do you use it without getting burned?**

The answer I've settled on is boring, and that's the point. It's a pattern, not a product. I call it **read-only by construction**, and I've been running it against my own homelab for weeks now. This post is the pattern explained — the thinking, the design, and the code — so you can copy it for your own setup in about fifteen minutes.

## The Tension, Restated

Let me recap the problem I spent 2,000 words on in August, because it's the whole reason this pattern exists.

MCP servers are *trusted* by design. An AI client connects, discovers the server's tools, and then calls those tools with arguments that are **influenced by whatever text the model is processing.** That text can come from a web page, an email, a PDF, or the output of another tool — and if any of it is attacker-controlled, the attacker steers the arguments your agent passes to your tools. Tools that, by design, can read files, query databases, and execute commands.

The scary part of that post wasn't the attack-surface stats. It was this: **even your own trusted MCP servers become dangerous the moment they touch untrusted data.** The trust boundary isn't the server — it's the data flowing through it.

So the question becomes: can you design an MCP server where hostile input *can't* cause harm, because the server has no harmful capability to begin with?

## The Read-Only Pattern

The answer is simpler than the security literature makes it sound:

> **Every tool is an HTTP `GET` / health probe. Nothing is written, mutated, or exfiltrated. The server holds no tokens, no credentials, no SSH keys — so there is nothing for an attacker to extract and nothing for an injected instruction to abuse.**

The worst thing my server can do, under any circumstances, is tell you a service is down. That's not a *sandbox* — it's a *property of the design*. You don't have to trust the model, the input, or the tool output, because there's no capability to reach.

Here's the concrete version. I run a homelab with a handful of self-hosted services scattered across a few machines — a torrent automation tool, a Soulseek client, a media manager, a hardware monitor, an \*arr stack. Keeping track of "is everything healthy?" means SSHing into boxes or clicking through half a dozen web UIs. It's the exact kind of repetitive, read-only status-checking an AI is good at — but I don't want to hand it SSH keys.

So I built a small MCP server that exposes those services as **queryable health probes**. Three tools:

| Tool | What it does |
|------|--------------|
| `list_services` | Return the configured service registry. No network calls. |
| `check_service` | Probe one service's health endpoint — status, latency, body preview. |
| `check_all` | Probe the fleet; return an UP / DEGRADED / DOWN summary. |

Plus one resource, `homelab://services`, that dumps the full registry as JSON.

That's it. No `run_command`, no `read_file`, no `execute_sql`, no egress. The entire tool surface is "ask, and I'll tell you whether it's alive." Ask your AI assistant *"is my homelab healthy?"* and it can actually check — without you giving it write access or credentials.

## Why "Config-Driven" Matters

The second design decision is the one that keeps this from becoming a maintenance burden: **the service registry is data, not code.**

```json
{
  "services": [
    {
      "name": "autobrr",
      "url": "http://192.168.1.50:7474",
      "healthUrl": "http://192.168.1.50:7474/api/healthz/liveness",
      "description": "autobrr — torrent/Usenet automation",
      "kind": "http"
    },
    {
      "name": "slskd",
      "url": "http://192.168.1.50:5030",
      "healthUrl": "http://192.168.1.50:5030/health",
      "description": "slskd — self-hosted Soulseek client",
      "kind": "http"
    }
  ]
}
```

Adding a service is **adding a JSON line** — no code changes. Removing one is deleting a line. The tool surface stays stable while the fleet changes under it. That's a small thing, but it's the difference between "I set this up once and it still works six months later" and "I abandoned it because every new service meant editing the server."

It also enforces the read-only property *structurally*. Because the only `kind` implemented today is `http` — and the only thing the server ever does is `GET` the `healthUrl` — there is no code path that writes. Future adapters (say, a Proxmox VM-status read via its read-only API) get added as a new `kind` + probe function, and the invariant stays: **probes only, never mutations.**

## The Code (Small Enough to Read in One Sitting)

The server is ~200 lines of Node using the official MCP SDK, and the core is almost embarrassingly simple. Here's the probe function — the whole thing the server *does*:

```js
async function probe(url, { timeoutMs = 4000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  const started = Date.now();
  try {
    const res = await fetch(url, { signal: controller.signal, redirect: "follow" });
    const body = await res.text().catch(() => "");
    return {
      ok: true,
      status: res.status,
      latencyMs: Date.now() - started,
      bodyPreview: body.slice(0, 400),
    };
  } catch (err) {
    return {
      ok: false,
      error: err.name === "AbortError" ? `timeout after ${timeoutMs}ms` : err.message,
      latencyMs: Date.now() - started,
    };
  } finally {
    clearTimeout(timer);
  }
}
```

A `GET`, a timeout, a status code, and a 400-character preview. That's the entire capability. The tools just call this and shape the result:

```js
function healthOf(p) {
  if (!p.ok) return "DOWN";
  if (p.status >= 200 && p.status < 400) return "UP";
  return "DEGRADED";
}
```

`DEGRADED` is worth calling out, because it's where the read-only pattern earns its keep in practice. Some services expose a cheap unauthenticated health endpoint (`/health`, `/api/healthz/liveness`); others only expose an authenticated API that returns 401 to a naked GET. Rather than stuff API keys into the server (which would break the "no secrets" invariant), those get reported as `DEGRADED` — which is *correct information*. The server never holds the keys, and the probe honestly tells you "reachable, but not readable without auth."

## Wiring It Up Is the Point

The whole reason to build this as an MCP server (rather than a cron job or a dashboard) is that it plugs into the AI tools you already use. Thirty seconds:

**Claude Code:**

```bash
claude mcp add homelab -- node /Users/you/homelab-mcp/index.js
```

Then ask *"is my homelab healthy?"* and watch it call `check_all`.

**Claude Desktop / Cursor** — add to the MCP config:

```json
{
  "mcpServers": {
    "homelab": {
      "command": "node",
      "args": ["/Users/you/homelab-mcp/index.js"]
    }
  }
}
```

Because it's stdio transport, the "auth" is the OS process boundary — the server runs as your user, on your trusted network, and binds nothing. No port, no token, no exposure.

## Why This Pattern Is the Antidote to My Own Warning

Let me tie this back to the attack-surface post, because that's the part I actually care about.

Every hardening rule in that post reduces to "make hostile input unable to cause harm." But I framed most of them as *process* — sandbox the agent, scope tools to least privilege, treat all tool output as untrusted. All correct, all necessary, all *things you have to remember to do*.

The read-only pattern is different. It's not a practice you maintain; it's a **property you build in.** You don't have to remember to scope the tools, because the tools have no dangerous capability to scope. You don't have to audit the supply chain with paranoia, because the server is 200 lines you can read in one sitting and it never writes, never phones home, and never reads a credential.

That's the insight, stated as plainly as I can: **the safest MCP server isn't the one you harden — it's the one that has nothing to lose.**

It's also why the "read vs. write" split I keep recommending matters more than any individual tool. A read-only agent that can't call a write tool is *provably* safe against prompt injection — there's no write tool to reach. This pattern is just that principle, applied to an entire server.

## The Limits (Honesty About What This Isn't)

I don't want to oversell this. A read-only status server is not a general MCP strategy:

- It doesn't help you if the thing you need is *write* access (deploying, provisioning, mutating). For that, you still need the full sandbox + least-privilege + output-sanitization stack from the attack-surface post.
- Read-only doesn't mean *read-anything*. If you expose a tool that reads arbitrary files or databases, "read-only" is still a data-exfiltration vector — the pattern only holds because the reads are narrow (health endpoints, not file contents).
- It's LAN-only by assumption. If you ever bind this to a remote/agent context, you've crossed a trust boundary deliberately, and the "no secrets" property is what keeps that from being a disaster.

But for a very common class of task — "what's the status of my stuff?" — read-only is the right tool, and it's safe enough to hand to an agent without a second thought.

## The Bottom Line

A few months ago I wrote that MCP is your new attack surface, and the fix was to treat it like the attack surface it is. This post is the other half of that answer: **the fix is also to make servers that don't have an attack surface.**

Give your AI eyes on your homelab — not the keys. Every tool an HTTP health probe. No tokens, no writes, no SSH. The worst it can do is tell you something's down, and honestly, that's the most useful thing it can do anyway.

The server is called `homelab-mcp`, it's on [GitHub](https://github.com/bryanmoon19), and it's ~200 lines you can read before you run it — which, given my last post, is exactly the point.

---

*If you run an MCP server in your homelab, try rewriting it read-only and see what actually breaks. My guess: nothing you miss. If you found this useful, the full arc is in [building your first MCP server](/blog/2026-07-21-mcp-for-homelab-build-first-server), [the attack-surface warning](/blog/2026-08-16-mcp-servers-attack-surface), and [running MCP on Cloudflare Workers](/blog/2026-10-23-mcp-server-cloudflare-workers/).*
