---
layout: post.njk
title: "The MCP Approval Gateway: Give Your AI Write Access (With a Human on the Trigger)"
date: 2026-11-07
description: "Read-only MCP servers are safe but limited — eventually you need an agent that can actually write, deploy, and mutate. The answer isn't blind trust or full lockdown: it's an approval gateway that holds every tool call for a human yes/no. Here's the landscape, the pattern, and how to wire one into your homelab."
tags: ["mcp", "model-context-protocol", "approval", "human-in-the-loop", "gateway", "self-hosted", "homelab", "security", "ai", "claude-code", "agent"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-07-mcp-approval-gateway-homelab/"
affiliate: false
cta: true
---

Last week I showed you the [read-only MCP pattern](/blog/2026-11-03-read-only-mcp-pattern-homelab/) — the trick of building an MCP server whose every tool is an HTTP health probe, so a hostile prompt literally can't cause harm because there's no write tool to reach. I called it "give your AI eyes on your homelab, not the keys."

I still believe that. But it left an obvious objection hanging, and a few of you emailed me about it: *"Eyes are nice, but what if I actually want the agent to **do** something?"*

Deploy a container. Restart a service. Provision a DNS record. Write a file. At some point, a useful AI agent needs to mutate state. And the moment you hand it a write tool, you've left the read-only garden and re-entered the world where [MCP servers are your attack surface](/blog/2026-08-16-mcp-servers-attack-surface).

The answer the ecosystem is converging on is neither blind trust nor full lockdown. It's a middle position with a name: **the approval gateway.** A layer that sits between your agent and its tools and holds every call for a human yes/no — human-in-the-loop, but only for the dangerous verbs.

This post is that pattern. It's the missing fourth chapter in the MCP arc I've been writing all year: build one, fear one, make one read-only, and now — make one *that can write, safely*.

---

## The Problem: Read-Only Is Safe *Because* It's Useless for Writes

Let me be honest about what the read-only pattern buys you and what it costs.

A read-only server is provably safe against prompt injection because there's nothing to inject *into* — no write path exists. That's the whole trick, and it's a good one. But "safe" and "capable" are on opposite ends of a dial, and read-only pins the dial at zero capability. You can ask it "is my Plex up?" all day. You can't ask it "restart the container that's crash-looping."

For most homelabbers, that's fine — 90% of what you want an agent to do is *look at things*. But the 10% that remains is exactly the 10% that would actually save you time: the restart, the deploy, the config change, the one-command fix.

The question isn't "how do I keep my agent from ever writing." It's **"how do I let it write, without it writing *unsupervised*?"**

That's a different question with a different answer.

---

## The Answer: An Approval Gate

The idea is simple enough to state in one line:

> **Every write-capable tool call passes through a gate that pauses the agent and asks a human to approve or deny — with full visibility into what's about to happen.**

You've actually seen this already if you've used Claude Code or Cursor. When the agent wants to run `rm -rf`, run a command, or hit a tool with side effects, it *stops and asks*. The approval gateway is that same instinct, generalized into a standalone layer you control — one that wraps *any* MCP server, not just the ones baked into a specific editor.

The payoff is the thing read-only can't give you: an agent that can actually do work, with a human as the final arbiter on every irreversible action. Not "safe because it can't write," but "safe because a person signs off on every write."

---

## The Landscape: Everyone Just Shipped One

The timing on this is telling. In the last year, "MCP gateway" went from a niche idea to a crowded category, and the security-flavored ones — the ones with approval and audit in the DNA — are the fastest-growing slice. Here's what's out there right now:

| Project | Stars | What it actually is |
|---------|-------|---------------------|
| **maximhq/bifrost** | 9,416 | Unified AI/MCP/LLM gateway — routing, failover, caching, virtual keys, budgets. The "control plane" take. |
| **samanhappy/mcphub** | 2,640 | Self-hosted MCP gateway + control plane for connecting and *operating* servers. |
| **docker/mcp-gateway** | 1,627 | Docker's official CLI plugin / gateway for MCP. |
| **agentic-community/mcp-gateway-registry** | 1,038 | Enterprise gateway + registry — OAuth, Keycloak/Entra, auditable, governed tool access. |
| **microsoft/mcp-gateway** | 911 | Reverse proxy + lifecycle management for MCP servers in Kubernetes. |
| **ThinkWatchProject/ThinkWatch** | 814 | Self-hosted AI/MCP gateway: SSO, RBAC, per-user tool identity, PII redaction, **tool-call guards**, rate limits, audit logs. |

Three things jump out of that table:

**First, the bar moved from "build a server" to "govern a fleet of them."** A year ago the pitch was "here's an MCP server for Stripe." Today the pitch is "here's a layer that sits in front of *all* your MCP servers and enforces policy." That's a maturity signal — the ecosystem realized that the scary part isn't any one server, it's the *unmanaged sprawl* of them.

**Second, the security angle is now the differentiator.** Look at the top of the list: bifrost (budgets, virtual keys), mcphub (control plane), ThinkWatch (PII redaction, tool-call guards, audit logs), the gateway-registry (OAuth, governed access). The ones people are actually adopting are the ones that answer "how do I let an agent use tools *without* handing it the keys." That's the approval-gateway instinct, productized.

**Third, the whitespace is the *self-hostable, auditable, human-in-the-loop* slice.** The enterprise players (Microsoft, the registry) assume you have Keycloak, Entra, Kubernetes, a security team. The small ones (a scattering of single-digit-star "mcp-approval-gateway" repos) are proofs of concept. In between is a gap: a gateway that a homelabber can run on one box, that pauses on writes and asks *you*, and that keeps an audit trail you can actually read. That gap is the opportunity — and it's the exact shape of the thing I want to run in my own lab.

---

## The Pattern, Concretely

Here's the approval-gateway pattern reduced to what actually matters, independent of any specific product:

**1. Classify every tool by risk.** Three buckets, no more:
- **Read** — safe, no approval. Health probes, reads, status queries. Fire freely.
- **Write / mutate** — approval required. Deploys, restarts, config writes, deletes. Always hold.
- **Deny** — never available to the agent, full stop. Anything that could exfiltrate secrets or touch money/identity.

The classification is *your* job and it's the single most important decision you make. Get it wrong and the gate is theater.

**2. Put the gate *between* the agent and the tools, not inside them.** The whole point of a gateway (vs. a read-only server) is that it's a *layer*, not a property of any one tool. You connect the agent to the gateway, the gateway connects to your real servers, and the gateway enforces policy. That way you get one approval surface for *everything*, instead of re-implementing "ask before writing" inside every server you write.

**3. The approval prompt has to show the *full* context.** A useful approval gate doesn't just say "approve `write_file`?" It shows: *what* tool, *what* arguments, *what* the agent said it's trying to do, and *why*. The difference between a good gate and a useless one is whether the human can make an informed call in two seconds. An approval prompt that says "allow tool call?" with no context is how you train yourself to click yes reflexively — which is worse than no gate at all.

**4. Keep an audit trail you can actually read.** Every approval and denial gets logged with a timestamp, the tool, the args, and the outcome. Not because you'll read it daily — because the day something goes wrong, you'll want the paper trail. "Auditable" isn't a buzzword; it's the difference between "what happened?" and "we don't know what happened."

**5. Default-deny for the dangerous verbs, default-allow for the reads.** You want the agent to *flow* on the safe stuff and *stop* on the scary stuff. If you make it ask permission to read a file, you'll be approving all day and the gate becomes noise. Save the friction for where it matters.

---

## How I'd Wire It Into a Homelab (Concrete)

If I were doing this today on my own lab — and this is the natural extension of the `homelab-mcp` server I shipped last week — here's the setup:

**Start from the read-only server you already trust.** `homelab-mcp` already has the health-probe tools (`list_services`, `check_service`, `check_all`) that should stay *read*. Those keep flowing with zero approval. This is your "eyes."

**Add the write tools behind a gate.** The moment you want `restart_service` or `deploy_stack` or `write_config`, you don't bolt them onto the read-only server and hope. You route them through an approval layer that holds the call, shows you the full context, and only executes on your yes. The write tools live *behind* the gate; the read tools live *in front* of it.

**Log every approval.** A simple append-only audit file — timestamp, tool, args, decision — is all you need. It's not glamorous, but it's the difference between "I think I approved that" and "here's the record."

**Escalate on irreversibility.** A restart is low-stakes (you can restart again). A `rm -rf` or a DNS deletion is not. Your gate should distinguish "annoying to undo" from "impossible to undo" and raise the friction accordingly — maybe require an explicit typed confirmation for the latter, not just a click.

The honest framing: **an approval gateway is read-only for everything *except* the handful of verbs where you've decided the risk is worth the capability.** It's not "trust the agent." It's "trust the agent to *propose*, and reserve the right to *veto*."

---

## The Honest Caveats

I want to be straight about what this doesn't solve, because the category is young and a lot of the marketing oversells:

- **An approval gate is only as good as your attention.** If you rubber-stamp every prompt, you've built a checkbox, not a control. The gate's security is *you*, and you will get tired of clicking. Design for that — approve the boring stuff in bulk, hold only the genuinely risky calls.
- **Prompt injection can still steer *which* call gets proposed.** A gate stops an agent from *silently* writing. It doesn't stop a hostile prompt from convincing the agent to *propose* a dangerous write that looks innocuous. The approval prompt's context display is your defense here — that's why it has to show the full call, not just the tool name.
- **The small/enterprise split is real.** The mature gateways assume SSO, Kubernetes, a security team. The homelab-grade ones are young. Don't expect a turnkey "approval gateway for your basement" that's as polished as the enterprise stuff — the space is still being built.
- **A gateway is a new thing to babysit.** You're adding a service that sits in front of your services. That's one more process, one more thing to update, one more thing that can break. For a homelab that already runs a dozen containers, that's a real cost — weigh it against the benefit honestly.

None of this kills the idea. It just sets the expectation: an approval gateway trades "provably safe because incapable" for "capable, with a human on the trigger." That's a better trade for the writes that actually matter.

---

## The Bottom Line

The read-only pattern I wrote about last week was the answer to "how do I use MCP without getting burned?" — and the honest answer was "make it so there's nothing to burn."

This post is the next question: **"and when I need it to actually *do* something?"**

The answer isn't to reopen the attack surface and trust the agent. It's to put a gate in front of it. Keep the reads flowing free, hold every write for a human yes, and keep a record of every call you approved and every one you didn't. Read-only where it's safe, human-in-the-loop where it isn't, auditable everywhere.

That's the fourth chapter: not "never write," and not "trust the agent" — but **"let it propose, and you decide."**

If you've been running read-only and hitting its limits, this is the upgrade path. Start by classifying your tools into read / write / deny. Then pick one gateway from the table above that matches your tolerance for self-hosting, and route a single dangerous verb through it this weekend. See if it feels like a safety net or a chore — that's the data you need to know whether the trade is worth it.

---

**Related posts:**
- [The Read-Only MCP Pattern: Give Your AI Eyes on Your Homelab](/blog/2026-11-03-read-only-mcp-pattern-homelab/)
- [MCP Servers Are Your New Attack Surface](/blog/2026-08-16-mcp-servers-attack-surface/)
- [Build Your First Self-Hosted MCP Server](/blog/2026-07-21-mcp-for-homelab-build-first-server/)
- [Build an MCP Server on Cloudflare Workers in 10 Minutes](/blog/2026-10-23-mcp-server-cloudflare-workers/)

---

*Links: [mcphub](https://github.com/samanhappy/mcphub) · [docker/mcp-gateway](https://github.com/docker/mcp-gateway) · [bifrost](https://github.com/maximhq/bifrost) · [microsoft/mcp-gateway](https://github.com/microsoft/mcp-gateway) · [ThinkWatch](https://github.com/ThinkWatchProject/ThinkWatch) · [homelab-mcp](https://github.com/Bryanmoon19/homelab-mcp)*
