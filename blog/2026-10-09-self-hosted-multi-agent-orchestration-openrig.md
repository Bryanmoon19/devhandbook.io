---
layout: post.njk
title: "OpenRig: The Missing 'Team Layer' for Your Self-Hosted AI Agents"
date: 2026-10-09
description: "We've covered solo agents, sandboxing, and memory — but never the orchestration layer that turns a pile of terminal sessions into a persistent agent team. OpenRig (6.2K stars, trending weekly) wraps Claude Code and Codex into YAML-defined teams with roles, shared context, and owned work. Here's how it works and how to self-host it."
tags: ["ai-agent", "orchestration", "multi-agent", "self-hosted", "homelab", "claude-code", "codex", "openrig", "automation", "developer-tools"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-09-self-hosted-multi-agent-orchestration-openrig/"
affiliate: false
cta: true
---

If you've been following this blog's AI-agent cluster, you've watched me cover the stack piece by piece. We did [solo coding agents](/blog/2026-06-16-self-hosted-ai-coding-assistants/), [sandboxing](/blog/2026-07-29-ai-agent-sandboxes-homelab/), [MCP servers](/blog/2026-07-21-mcp-for-homelab-build-first-server/), and even the [trust problem](/blog/2026-08-18-ai-code-review-checklist/). But there's been a hole in the middle of that picture, and it's been bugging me for months.

We've talked about *one* agent doing *one* thing. What we've never covered is the **team layer** — the orchestration that turns a scattered pile of terminal sessions into a persistent, organized crew with roles, shared context, and work that survives a reboot.

That's what **OpenRig** is. It's sitting at 6.2K stars on GitHub and trending weekly, and it's the piece I've been missing.

## The Gap, Stated Plainly

Solo agents are great until you hit the limits:

1. **No division of labor.** One agent does everything — writing, reviewing, testing. Which means the reviewer is the same "person" who wrote the code. That's how you get [the Snowflake situation](/blog/2026-08-18-ai-code-review-checklist/) — nobody independent catches the bug.

2. **No persistence.** Your agent's context lives and dies with the terminal session. Close the window, lose the team. Every new session is a stranger that needs the whole story retold.

3. **No shared memory.** Five separate agent sessions each have their own picture of the project, and none of them agree.

OpenRig's pitch is one sentence that sums up the fix: **"A harness wraps a model. A rig wraps your harnesses."** You define your agent team in YAML, boot it with one command, and Claude Code and Codex sit in the *same rig*, managed as one system.

## What OpenRig Actually Is

OpenRig is open-source (Apache 2.0) software for building and running your own network of agents. It's the system behind the creator's ([@_feralmachine](https://x.com/_feralmachine)) "AI civilization" experiments, and it's built to be self-hosted on macOS or Linux (WSL2 on Windows).

The core idea:

- **Rig** — your agent team, defined as a YAML "RigSpec."
- **Pods** — logical groupings of agents (e.g. `orch`, `dev`, `qa`).
- **Seats** — individual agent instances, each wrapping a harness (Claude Code or Codex).
- **Edges** — the topology connecting seats, defining who can talk to whom.
- **Operator** — a lead agent you converse with about outcomes, which coordinates the specialists.

You don't manage seven terminal windows. You talk to one lead agent, and it delegates to the team.

### The three built-in teams

OpenRig ships with three starter teams, scaled to your ambition:

| Team | Talk to | Agents | For |
|------|---------|--------|-----|
| `starter` | `dev-build@starter` | A Claude Code builder + Codex reviewer | One bounded change |
| `workshop` | `orch-lead@workshop` | Lead, builder, QA, reviewer | Ongoing work in one repo |
| `factory` | `orch-lead@factory` | Seven: lead, advisor, build, QA, design, two reviewers | Sustained product work |

The `starter` team alone fixes the biggest hole in solo-agent workflows: it pairs a **Claude Code builder with a Codex reviewer**, so the reviewer is a genuinely different model with a different perspective. That's a real separation of concerns, not one model grading its own homework.

## Installing It

The install is one command (with a `--dry-run` to preview first):

```bash
curl -fsSL https://raw.githubusercontent.com/mvschwarz/openrig/v0.6.8/scripts/install.sh | sh -s -- --dry-run
curl -fsSL https://raw.githubusercontent.com/mvschwarz/openrig/v0.6.8/scripts/install.sh | sh
```

Or, step by step:

```bash
npm install -g @openrig/cli
rig setup --dry-run
rig setup
```

**Requirements:** Node.js 22 or 24, plus `tmux`. On a Mac with Apple silicon, use Node 22 (there's a known compatibility limitation). You also need an existing **Claude Code or Codex** account — OpenRig reuses your subscriptions rather than selling you a new one. Sign in once with `claude auth login` or `codex login` and you're done.

After install, your agent (or the `rig` CLI) opens the OpenRig TUI and the operator for you. You can get back to it anytime with:

```sh
rig daemon start
rig terminal open saved:kernel --window
```

`rig tui` gives you the team dashboard — a graph of the rig, then a table of seats showing runtime, model, context, and state per seat.

## Launching Your First Team

The manual path (no operator hand-holding) is three commands from inside your repo:

```bash
cd /path/to/your/repository
rig specs preview starter --kind rig
rig up starter --cwd . --plan
rig up starter --cwd .
```

Then check readiness and hand the builder a bounded task:

```bash
rig ps --nodes --rig starter
rig send dev-build@starter 'Implement <one useful change>. Track the task in the queue and return its ID. Keep it local, verify the behavior, ask dev-review in this rig to check the exact candidate, and record the result and how I can try it.'
rig queue list --destination dev-build@starter --limit 1000
```

Notice the shape of that message: a *bounded outcome*, not an open-ended "do stuff." That's the discipline OpenRig enforces — you're managing a team, not throwing prompts into the void.

## Defining Your Own Team in YAML

The real power is the RigSpec. Here's a minimal valid example:

```yaml
version: "0.2"
name: my-rig

pods:
  - id: dev
    label: Development
    members:
      - id: build
        agent_ref: "local:agents/impl"
        profile: default
        runtime: claude-code
        cwd: "."
    edges: []

edges: []
```

And a more complete one — a product squad with orchestration and review pods, startup files, and continuity policy:

```yaml
version: "0.2"
name: my-product-team
summary: A full product squad with orchestration, development, and review pods.

docs:
  - path: SETUP.md
  - path: README.md

pods:
  - id: orch
    label: Orchestration
    members:
      - id: lead
        agent_ref: "local:agents/orchestrator"
        runtime: claude-code
      - id: peer
        agent_ref: "local:agents/orchestrator"
        runtime: codex
    edges: []

  - id: dev
    label: Development
    continuity_policy:
      enabled: true
      sync_triggers: [pre_compaction, pre_shutdown]
      artifacts:
        session_log: true
        restore_brief: true
      restore_protocol:
        peer_driven: true
    members:
      - id: build
        agent_ref: "local:agents/impl"
        runtime: claude-code
        cwd: "."
        model: claude-opus-4-6
        restore_policy: resume_if_possible
    edges: []

edges: []
```

Two things here are worth calling out because they're what separates a *team* from a script:

**`continuity_policy`** — this is the persistence layer. It syncs session logs and restore briefs before compaction or shutdown, so a seat can resume work rather than starting cold. This directly answers the "context dies with the terminal" problem.

**`edges`** — the topology. You control who talks to whom. The lead coordinates; the builder and reviewer talk through the lead, not directly to each other in an unbounded free-for-all. That structure is what keeps a multi-agent system from turning into chaos.

## The Honest Trade-offs

OpenRig is genuinely new and genuinely powerful, but let me be straight about the friction, because I'd want to know it before installing:

**It writes things to your machine.** This is a real consideration. Setup touches `~/.tmux.conf`, installs a terminal multiplexer (Herdr), seeds skills into `~/.claude/skills` and `~/.agents/skills`, and writes Codex hook config and trust records. It also launches a **daemon** with instance state under `~/.openrig`. The README has a full table of what changes and why — read it before running. Nothing is hidden, but this is not a zero-footprint tool.

**Permissions are a real thing to think through.** A team seat with no permission policy gets a per-launch "team default" — Claude can run ordinary `rig` commands and project reads without prompting, while lifecycle commands like `rig up`/`rig down` still ask. OpenRig explicitly *does not* add global YOLO allow rules by default. That's the right call, and it's why you should read the permission-policy docs rather than blindly accepting the "workshop bundle" that ships with broad access.

**It's opinionated about your harnesses.** You're building on Claude Code and Codex — there's no abstract "bring any model." If you're not already in one of those ecosystems, that's a decision to make, not a bolt-on.

## Where It Fits in the Stack

I've been building toward this without realizing it. Here's how OpenRig slots into the self-hosted AI-agent picture:

- **The sandbox layer** (Dormice, Firecracker, Docker) keeps *individual agents* from wrecking your machine.
- **The memory layer** (whatever you're using for shared context) gives agents something to remember.
- **OpenRig is the layer on top** — the orchestration that assigns roles, routes work, and keeps the team's context at stable addresses across sessions.

None of those replace the others. OpenRig is the thing that was missing: a way to run *more than one* agent as a *coordinated system* rather than a pile of parallel soloists.

## Is It Worth It?

If you're happy with one agent doing one task in one terminal, OpenRig is overkill — stick with what you've got. But if you've ever:

- caught yourself copy-pasting context between three agent windows,
- wished your "reviewer" wasn't the same model that wrote the code,
- or wanted your agent work to survive a reboot with its memory intact,

…then this is the missing piece, and it's trending for a reason. It's the first self-hosted orchestration layer I've seen that treats an agent team as a *first-class, persistent system* instead of a clever bash script.

I'll be digging deeper into OpenRig's rig-spec and continuity policies in a follow-up. For now, the getting-started guide at [openrig.dev](https://openrig.dev) is the place to start — install, talk to the kernel operator, and pick a team for your first useful change.
