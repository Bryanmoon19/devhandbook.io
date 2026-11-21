---
layout: post.njk
title: "Agent Skills (SKILL.md): The Missing Bridge in Your AI-Coding Cluster — and How to Build, Version, and Self-Host Your Own"
date: 2026-11-21
description: "Agent Skills — the SKILL.md format that gives your AI coding agents reusable, promptable procedures — is exploding (multiple 300–700+ point HN threads, GitHub trending saturated with skill repos), yet it's the one layer of the AI-coding stack nobody has written a self-hoster's guide to. Here's what SKILL.md actually is, why it beats raw system prompts and MCP for the 'how I do this task' layer, how to build, version, and self-host your own skills, and a free SKILL.md linter that catches the mistakes that break real skills before you ship them."
tags: ["agent-skills", "skill-md", "claude-code", "claude-skills", "ai-coding", "llm-agents", "mcp", "prompt-engineering", "developer-tools", "self-hosted", "ai-agents", "cursor", "openclaw", "local-llm"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-21-agent-skills-skill-md-guide/"
affiliate: false
cta: true
---

# Agent Skills (SKILL.md): The Missing Bridge in Your AI-Coding Cluster — and How to Build, Version, and Self-Host Your Own

Your AI-coding cluster has a gap in it, and it's the one nobody's talking about.

You've wired up the model. You've pointed Claude Code (or Cursor, or OpenClaw, or a local LLM through Ollama) at your repo. You've got MCP servers feeding it tools — files, git, a browser, your database, maybe your whole homelab. The agent can *see* everything and *do* everything.

And yet every time you ask it to do the same non-trivial task you asked it to do last week — "set up a new LXC container with this exact firewall pattern," or "run the pre-release checklist on this library," or "migrate this service's config the way I like it" — it re-derives the procedure from scratch. Sometimes it nails it. Sometimes it confidently does the thing *almost* right and you spend twenty minutes catching the drift.

That gap — between "the agent has the tools" and "the agent has *your* procedure" — is exactly what **Agent Skills** (the `SKILL.md` format) exists to fill. It went from obscure to inescapable over the last several weeks: multiple HN threads in the 300–700+ point range, GitHub trending pages saturated with skill repos, entire ecosystems sprouting `skills/` directories. And yet devhandbook.io — which has written ~20 posts on AI agents and local LLMs — has somehow never covered it. Let's fix that, properly, with the build/version/self-host guide the format deserves.

---

## What a SKILL.md Actually Is

Strip away the hype and an Agent Skill is a shockingly simple thing: **a single Markdown file** (almost always named `SKILL.md`) containing a YAML frontmatter block and a body, that teaches an agent a *reusable procedure*. That's the whole format. Here's a minimal one:

```markdown
---
name: lxc-provision
description: Use when the user asks to set up a new LXC container on Proxmox
  with the homelab's standard firewall, SSH-key, and mount conventions. Produces
  a working container matching the house pattern.
---

# LXC Provisioning

## Steps

1. Confirm the container ID, hostname, and intended service with the user.
2. Create the container with `pct create` using the pinned Debian template.
3. Apply the standard firewall rules from `templates/lxc-firewall.conf`.
4. Mount the NAS share and install SSH keys from `templates/authorized_keys`.
5. Verify with `pct status` and a fresh SSH login, then report the IP.
```

That's it. Name. Description. Steps. The agent reads it when the task matches the description, and now it has *your* procedure instead of a half-remembered guess.

The key insight that makes this a real format rather than just "a prompt in a file" is the **`description` field is the trigger.** It's not decorative metadata. It's the routing rule: the agent scans its available skills, matches your request against the descriptions, and loads the one whose description says "use when the user asks to do X." A skill with a vague description might as well not exist, because the agent will never know when to load it.

That one detail is why skills feel different from everything that came before, and it's the source of most of the format's sharp edges. More on that in a moment.

---

## Why SKILL.md Beats System Prompts and MCP for the "How" Layer

To understand where skills fit, it helps to map the AI-coding stack by what each layer is *for*:

- **The model** is the reasoning engine.
- **MCP servers** (which we've covered at length — see our [MCP server guide](https://devhandbook.io/blog/2026-07-21-mcp-for-homelab-build-first-server/) and the [MCP attack-surface post](https://devhandbook.io/blog/2026-08-16-mcp-servers-attack-surface/)) are the *capabilities* — the tools and data sources the agent can reach.
- **System prompts** are the *persona and constraints* — the always-on rules.
- **Agent Skills** are the *procedures* — the "how I do this specific task, in this order, to this standard."

The first three have been well-trodden. Skills are the layer that was missing, and the reason they arrived now is that the first three all have the same failure mode: **they don't compose.**

You can't easily share "how I provision an LXC the way *I* like it" as a system prompt, because a system prompt is a global blob — dump ten procedures into it and they all fight for the model's attention on *every* request, bloating context and diluting the important stuff. You can't easily do it as an MCP tool, because MCP tools are *capabilities*, not *recipes* — a tool does a thing; it doesn't encode the judgment about *when* and *in what order* to do things. (You *can* build a tool that does the whole procedure, but then you've written a script, not taught the agent the procedure — and you've lost the ability to adapt it conversationally.)

Skills compose because they're **lazily loaded, on-demand, by trigger.** A skill that isn't relevant to the current request costs nothing — it's just a description sitting in a directory. A skill that *is* relevant gets pulled into context whole, giving the agent the exact procedure with no dilution. You can have fifty skills and it behaves like you have none until the right one fires. That's the bridge: *capability without permanent context tax.*

There's a second, subtler reason skills caught fire: **they're the first agent-configuration artifact that's genuinely portable and shareable.** A system prompt is personal. An MCP server is infrastructure you have to run. A skill is a *file* — it travels in a git repo, it diff's cleanly, it can be reviewed as a PR, forked, vendored, and composed. It's the moment agent configuration stopped being "a thing I typed into a settings box" and became *code*.

---

## The Honest Catch (and Why the Linter Exists)

Here's the part the breathless "skills are the future!" posts skip, and it's why I built a tool for it.

The SKILL.md format is simple to *read* and genuinely easy to write *badly.* Because the whole mechanism hinges on the `description` trigger and on disciplined, imperative steps, a skill that's "almost right" fails *silently*. It doesn't crash. It just never gets loaded, or gets loaded and produces vague output. The failure modes:

1. **A description that doesn't lead with triggers.** If the description says "This skill helps with containers" instead of "Use when the user asks to set up or troubleshoot an LXC container," the agent's matching has nothing to latch onto. Your skill sits unused while the agent wings it.

2. **Oversized files.** A SKILL.md that balloons past ~10 KB (because you pasted a giant reference table or a wall of example output into the body) costs real context every time it fires. Skills are supposed to be *lean* — procedures with pointers, not encyclopedias.

3. **Vague or waffling steps.** "Optionally, you might want to check the logs" is not a step; it's noise. Skills work because each step is a positive imperative with a checkable completion criterion. Filler words (`just`, `simply`, `basically`) and restated defaults dilute the exact thing the agent needs: unambiguous, ordered actions.

4. **Restating defaults.** A skill that spends half its body telling the agent "be careful" and "use best practices" is wasting the tokens it cost to load. The model already does that. A skill earns its context only by changing behavior.

None of these are fatal to a human reader. All of them are fatal to a *trigger-and-load* pipeline. Which is exactly the kind of thing you want caught before you ship a skill into a directory that half your team's coding agents are going to load.

That's the gap **[our SKILL.md linter](https://devhandbook.io/skill-linter/)** fills. Paste a `SKILL.md` and it checks, client-side, the structural rules that actually matter to the format: valid YAML frontmatter with a `name` and `description`, description length and leading-trigger convention, the 10 KB size budget, presence and quality of a numbered `## Steps` section, waffling/optional step language, vague filler words, restated-default repetition, and reference-section placement. It's a heuristic guide, not a hard gate — a clean skill can still be wrong for its job — but it catches the silent failures before they go live.

---

## Building Your First Skill (the Right Way)

Here's the pragmatic workflow I've settled into, whether you're on Claude Code, Cursor, OpenClaw, or a local model.

### Step 1: Don't start with the format — start with the *friction*

The worst way to build skills is to brainstorm "what procedures should I write down?" That gets you a directory of abstractions nobody loads. The right way is to *notice* the friction: the moment you catch yourself re-explaining the same thing to your agent, or correcting it for drifting from your convention, that's a skill trying to be born.

Concrete triggers to watch for:

- You said "no, do it the way I did for the last one" this week.
- You have a checklist (release, deployment, onboarding, security review) you keep pasting into the chat.
- Your team has an undocumented convention ("always use `uv` here," "never commit generated files," "mounts go in this order").
- You find yourself writing the same 40-line instruction block across sessions.

Each of those is a skill with a ready-made description: "Use when…" is literally the sentence you keep typing.

### Step 2: Write it lean, with a real trigger

The skeleton above is the template. Three things matter more than everything else:

- **The description leads with the trigger.** First clause: when to use it. Second clause: what it produces. Keep it under ~1024 characters, ideally well under.
- **The body is a procedure, not a lecture.** Every step is a numbered imperative with a completion criterion you could actually check ("verify with `pct status`," not "make sure it works").
- **Reference material goes in bundled files, not the body.** A `templates/` directory, a `reference.md`, a `CLAUDE.md` — anything heavy gets pointed to from a step, never pasted inline. This is how you stay under the 10 KB ceiling while keeping the skill complete.

### Step 3: Lint it before you ship it

Before a skill goes into your `skills/` directory, run it through the [linter](https://devhandbook.io/skill-linter/). It'll flag the silent failures — the missing trigger, the oversized body, the waffling step — in seconds, with concrete fixes. Treat it like you'd treat a linter in any other code pipeline: not a style nanny, but a guard against the failure modes that are cheap to catch and expensive to debug once an agent is mis-loading skills in production.

---

## Versioning and Self-Hosting Your Skills

This is where the "skills are code" idea pays off, and where most teams stall because they treat skills like settings instead of like source.

### Put them in git, with the rest of the repo

A skill lives next to the code it operates on. If you have a homelab repo, the `skills/lxc-provision/SKILL.md` belongs *in that repo*, versioned alongside the templates and configs it references. That gives you:

- **Diffable procedures.** `git log` on a skill is a changelog of how your house procedure evolved.
- **Reviewable changes.** A change to "how we deploy" becomes a PR someone can actually review, not a settings tweak nobody saw.
- **Rollback.** A bad skill edit is one `git revert` away, same as a bad code edit.

This is the single biggest mindset shift, and it's the one that separates "I have some skills" from "skills are part of my stack."

### A shared, self-hosted skills library

Once skills are files, the obvious next step is a *library*: a repo of skills you and your team (or your other machines) all load. This is what's been flooding GitHub trending — collections of production-quality skills for everything from cloud deployment to security review.

The self-hosting pattern is simple and it's the same one you'd use for any dotfiles repo:

1. Create a repo (or a directory) of skills, each in its own folder: `skills/<name>/SKILL.md`.
2. Point your agent's skills directory at it — either by cloning it into the agent's expected location, or symlinking a shared location so every machine pulls the same canonical copies.
3. When you update a skill, push it, and every agent that consumes that directory picks up the change on its next load. No per-machine settings drift.

For OpenClaw specifically, skills live under `~/.openclaw/workspace/skills/` (and the bundled ones under the install path), and the same "it's just files in a directory" rule applies — you can version and share them like anything else. The exact path differs per agent, but the *pattern* is universal: skills are files, files are versionable, versionable things go in git.

### Don't over-collect

The failure mode on the other end of the spectrum: a skills directory with 80 entries, half of which you wrote once and never triggered again. Skills have a *carrying cost* — every skill's description is one more thing your agent scans on every request, and a bloated directory makes trigger-matching sloppier. Curate. If a skill hasn't fired in a few weeks, archive it. A short, sharp, actually-used set of ten skills beats a hundred dusty ones.

---

## The Bigger Picture: Your Agent's "How" Is Becoming Code

Zoom out and Agent Skills are the same arc we've watched hit every other layer of the stack. Infrastructure went from clicking to Terraform. Deployment went from ad-hoc scripts to declarative manifests. Documentation went from hand-drawn diagrams to diagram-as-code (which we covered in the [homelab-diagram post](https://devhandbook.io/blog/2026-11-20-homelab-diagram-as-code/)). And now, finally, *the way you teach your agent to do a task* is becoming a file — diffable, reviewable, shareable, lintable.

The reason it's spreading this fast is that it closes a loop that's been open since coding agents shipped: you could give an agent *tools* and *persona*, but you couldn't give it *your judgment about the work* in a way that composed. Skills are that missing piece. And because they're files, the entire ordinary software toolchain — git, linters, review, CI — suddenly applies to your agent's behavior in a way it never did before.

The HN threads and the trending repos aren't hype. They're the community collectively realizing that the last piece of the AI-coding cluster — the reusable, portable, versionable procedure — has an obvious shape, and it's a Markdown file with a name, a description, and a list of steps.

---

## What I'd Actually Recommend

If you're an AI-coding user and you don't have any skills yet, here's the concrete plan:

1. **Spend a week just *noticing*.** Every time you re-explain a procedure or correct a drift, write down the "use when…" sentence. That's your candidate list.
2. **Write three skills** — your three most-repeated procedures — using the skeleton above, keeping each under ~10 KB with reference material in bundled files.
3. **Lint them** with the [SKILL.md linter](https://devhandbook.io/skill-linter/) before they go live; fix the trigger, size, and waffling flags it surfaces.
4. **Put them in the repo they operate on**, or a shared skills library repo, and point your agent's skills directory at it. Treat changes as PRs.
5. **Curate monthly.** Archive skills that haven't fired; split any that got over 10 KB; rewrite descriptions that are drifting from "trigger + outcome."

The format is small enough to learn in an afternoon and the payoff compounds — every skill you ship removes one more "let me re-explain this" from every future session. Your AI-coding cluster stops being a pile of tools with a smart model on top, and starts being a system that actually *knows how you work*.

---

*Built a skill library you're proud of, or hit a SKILL.md failure mode the linter should catch? I'd genuinely like to see it — find me on [GitHub](https://github.com/Bryanmoon19), or paste your `SKILL.md` into the [linter](https://devhandbook.io/skill-linter/) and tell me what it missed.*
