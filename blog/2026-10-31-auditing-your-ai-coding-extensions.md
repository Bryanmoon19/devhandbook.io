---
layout: post.njk
title: "You Already Installed the Backdoor: Auditing Your AI Coding Extensions"
date: 2026-10-31
description: "A backdoor shipped through the Cursor extension/MCP marketplace hit 843 points on Hacker News this week. The lesson isn't just 'don't install sketchy extensions' — it's that the supply chain you've already installed needs auditing, right now. Here's the remediation playbook."
tags: ["cursor", "mcp", "security", "supply-chain", "ai", "backdoor", "extensions", "marketplace", "audit", "developer-tools", "remediation"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/auditing-your-ai-coding-extensions"
---

This week an 843-point Hacker News story put a name on something I've been warning about for months: **a backdoor shipped through the Cursor extension/MCP marketplace.**

I won't bury the lede on what happened, but the *news* is not the point of this post. By the time you read this, Cursor (or whoever the vendor is) will have pulled the malicious package, published an incident report, and moved on. The news cycle has a half-life measured in hours.

The part that stays with you is the part you can't uninstall with a click: **you've been installing AI-coding extensions and MCP servers for months, from authors you've never met, running code with your credentials, your environment variables, and your network access.** The backdoor that made the news is one instance of a much bigger question nobody's been asking:

*What's already installed, and how do I know it's not also a backdoor?*

That's the remediation playbook this post is about. Not the story. The cleanup.

## The Story, in One Paragraph (So You Can Skip It)

An extension in the Cursor marketplace — either an MCP server or an extension that wrapped one — was found to contain malicious code. The specifics vary by which of the threads you read: some say it was exfiltrating environment variables (`.env` files, API keys, cloud credentials), some say it was phoning home with file paths and partial source, some say it was a delayed second-stage payload that only activated after a grace period to slip past initial review.

The details matter less than the mechanism, because the mechanism is the same one I laid out in my [MCP servers attack surface](/blog/2026-08-16-mcp-servers-attack-surface) post: **a "helpful" tool is code running with your trust.** The marketplace gave it a storefront, a download count, and a five-star rating — and that was enough for thousands of developers to install it without reading a line of it.

The 843 points weren't because the backdoor was novel. They were because it landed in the place developers *feel* safest: inside their editor, next to the AI they already trust.

## Why the Marketplace Changes Everything

Before marketplaces, installing an MCP server or a coding extension meant cloning a repo, reading it, and wiring it up yourself. That friction was a *security feature*. You couldn't accidentally run arbitrary code — you had to type the command yourself, and in doing so you'd see what you were running.

The marketplace removed that friction, and with it, the review step. Now installing an extension is a button click in a UI that looks like the app store you use for everything else. Your brain applies the app-store heuristic — *"this was reviewed, this is safe"* — to a supply chain that has no such guarantee.

But here's the thing that makes it worse than a phone app store: **the threat model is inverted.**

A malicious phone app is sandboxed. It asks for permissions, the OS mediates, and even then it can't read your other apps' data. A malicious coding extension or MCP server is the *opposite*. It runs with your developer privileges, in the same process or the same machine as your code, your keys, and your repos. It doesn't need to *ask* for your `.env` — it can just read it. It doesn't need to *request* network access — it already has it.

The marketplace didn't just make bad actors easier to install. It made them more dangerous when installed.

## The Part Nobody Talks About: You Can't Trust the Marketplace Either

Let me be blunt, because this is the part of the story that got lost in the 843 points.

**The marketplace review process is not a security boundary.**

Cursor's marketplace — and every other AI-tool marketplace — is a distribution channel, not a security audit. Even in the best case, the review is a *first-pass* check: does this look like it does what it says, does it contain anything obviously malicious. It is not, and cannot be, a guarantee that the code is safe.

Three reasons:

1. **Delayed payloads.** The malicious code that gets reviewed is not necessarily the code that runs. A second-stage payload that activates after a delay, or after detecting a real developer environment, sails right past a review that only sees the first stage. This is a classic malware technique, and it works just as well in a marketplace as it does in a phishing email.

2. **Obfuscated intent.** A backdoor that exfiltrates environment variables looks almost identical to legitimate code that reads environment variables — because that's a thing MCP servers legitimately do. The difference is what it *does* with them (sends them to a remote server), and that's one line in a thousand. Review catches it only if a human is reading carefully and looking for exactly that.

3. **Volume.** The marketplace is growing faster than any review team can keep up. The "21,000 MCP servers exposed" number from my earlier post has only gone up, and the marketplace is adding more every day. Review at that volume is triage, not audit.

The practical takeaway: **you are the security boundary, not the marketplace.** The marketplace's job is distribution. Your job is trust — and you're the only one who can actually do it.

## The Audit: What to Do Right Now

So. The backdoor is in the news, the marketplace is a distribution channel, and you've got months of accumulated extensions and MCP servers installed. Here's the remediation playbook, ordered by impact.

### Step 1: Inventory Everything You've Installed

You can't audit what you can't see. Make a list of every AI-coding extension, MCP server, and plugin you've installed across every tool: Cursor, Claude Code, VS Code, Windsurf, Continue, anything.

For each one, record:

- **Name and publisher** — who claims to have made it?
- **Where it came from** — marketplace, npm, pip, git clone, a colleague's repo?
- **When you installed it** — and whether you actually use it.
- **What it claims to do** — in one sentence.
- **What it actually needs** — permissions, environment access, network egress.

The last item is where you'll find surprises. A "syntax highlighter" that reads your `.env` is a red flag. A "code formatter" that makes outbound network requests is a red flag. Most extensions will look reasonable on the surface — the audit is about finding the ones that don't match their own description.

### Step 2: Read the Source. All of It.

This sounds heavy, but it's usually smaller than you think. A typical MCP server is a few hundred to a few thousand lines. An extension wrapper is often a single file.

The goal isn't line-by-line comprehension — it's answering a small set of specific questions:

1. **Does it make network requests?** Search for `http`, `https`, `fetch`, `axios`, `requests`, `curl`, `socket`. Where does it connect, and why?
2. **Does it read sensitive data?** Search for `env`, `environment`, `.env`, `secret`, `token`, `key`, `password`, `credential`. What does it read, and what does it *do* with it?
3. **Does it execute code or shell commands?** Search for `exec`, `spawn`, `subprocess`, `system`, `eval`, `child_process`. What runs, and under what conditions?
4. **Does anything look obfuscated or delayed?** Long base64 strings, `eval` of encoded data, timers or delays before a network call, code that only runs under specific conditions.

The pattern you're looking for is **data flowing out that shouldn't.** An extension that reads your env and *sends it somewhere* is the whole ballgame. An extension that reads your env and *uses it locally* (e.g., to configure a tool) is fine.

### Step 3: Check the Publisher's History and Reputation

Marketplace badges and star ratings are trivially gameable — bought reviews, bot downloads, account farms. They tell you almost nothing.

What tells you something:

- **Is there a real, identifiable human behind it?** A GitHub profile with history, a blog, a presence in the community. An anonymous publisher with no footprint is a yellow flag.
- **Does the source repo have meaningful history?** A repo created three days ago with one giant commit and no issues or discussions is suspicious. A repo with months of commits, PRs, and issue responses suggests a real project.
- **Has anyone you trust vouched for it?** Not "has anyone starred it" — has a developer you know and trust actually read the source and used it in production?
- **Is the package name suspicious?** Typosquatting is rampant — names that are one character off from a popular package, or that sound generically legitimate ("cursor-utils", "mcp-helper") but have no real community behind them.

None of these are proof of anything by themselves. They're signals, and the combination matters.

### Step 4: Audit at Runtime, Not Just at Rest

Static review catches a lot, but not everything — and it doesn't catch the delayed-payload pattern at all. You also want to see what your extensions *actually do* while they run.

Three practical tools for this:

**1. Watch the network.** If an extension or MCP server is phoning home, the network will show it. Tools like `mitmproxy`, `Charles`, or even a simple `lsof -i` while you work will reveal outbound connections. An extension making a connection to a domain you don't recognize, at a time you don't expect, is the single clearest signal of a problem.

```bash
# While you're working, watch what your editor's extensions are connecting to
lsof -i -P -n | grep -iE "cursor|claude|code|node" | grep ESTABLISHED
```

**2. Watch the filesystem and environment.** The other half of a backdoor is what it *reads*. Filesystem access monitoring (`fs_usage` on macOS, `inotifywait` on Linux) will show you when an extension reads `.env`, your SSH keys, your AWS credentials, or anything else it has no business touching.

**3. Run it in a sandbox first.** Before trusting an extension on your real machine, run it in a container or a VM with *fake* credentials and *fake* data. If it's exfiltrating, the fake data is what leaks — and the network monitoring catches it. This is the runtime version of my [AI agent sandboxing](/blog/2026-08-09-ai-agent-sandboxing-homelab) argument: prove it's safe in a place where it can't hurt you, before you give it the real thing.

### Step 5: Remove What You Don't Use, and Pin What You Keep

The audit will surface extensions you installed once, used for a day, and forgot about. Those are the highest-risk items in your inventory — not because they're malicious, but because they're *unwatched*. You're not reviewing them, you're not updating them, and if one of them has a vulnerability or a backdoor, you'll never notice.

**Delete what you don't use.** Ruthlessly. An extension you're not actively using is pure liability.

For what you keep:

- **Pin the version.** Don't let extensions auto-update to whatever the latest is. Review an update the same way you reviewed the original, then bump the pin manually.
- **Review diffs on update.** An update is the single most common place a backdoor gets *introduced* — a maintainer gets compromised, or sells out, and the "legitimate" extension you audited six months ago ships a payload in a routine update. Treat every update as a new supply-chain decision.
- **Prefer source you control.** If you can, run the extension from a pinned git commit or a vendored copy rather than the marketplace's auto-updating version.

## The Playbook, Compressed

The whole thing fits on a card:

1. **Inventory** every extension and MCP server across every tool.
2. **Read the source** — look for network egress, secret reads, code exec, and obfuscation.
3. **Check the publisher** — real human, real history, real vouching, real name.
4. **Audit at runtime** — watch network and filesystem, sandbox first with fake data.
5. **Remove the unused, pin the kept, review every update.**

## Why This Is a *You* Problem, Not a *Cursor* Problem

I want to be careful not to let this become a "Cursor is bad" post, because that's the wrong conclusion and it'll leave you vulnerable in a different way.

The backdoor didn't exploit a Cursor vulnerability. It exploited the *trust model* that all of us — every AI-coding-tool vendor, every marketplace, every developer — have been quietly accepting: **that installing a tool from a storefront means it's safe.**

That trust model was always wrong. The marketplace is a distribution channel, not a security boundary. It will not keep you safe, and it never could. The only thing that keeps you safe is the audit — the deliberate, boring, unglamorous work of reading what you run and watching what it does.

The developers who get burned by the *next* backdoor won't be the ones who read the news. They'll be the ones who read the news, assumed the vendor fixed it, and went back to installing extensions with a single click.

The developers who *don't* get burned will be the ones who took this moment — this 843-point story — as a prompt to go inventory their own machines.

Go inventory yours tonight. The most likely finding isn't a backdoor. It's a dozen extensions you installed and forgot, any one of which could become one.

---

*Have you audited your installed extensions? Did you find anything that made your stomach drop? I'd love to hear about it — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on the [MCP servers attack surface](/blog/2026-08-16-mcp-servers-attack-surface), [building your first self-hosted MCP server](/blog/2026-07-21-mcp-for-homelab-build-first-server), the [AI code review checklist](/blog/2026-08-18-ai-code-review-checklist), and [AI agent sandboxing](/blog/2026-08-09-ai-agent-sandboxing-homelab).*
