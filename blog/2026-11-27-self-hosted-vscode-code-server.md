---
layout: post.njk
title: "Self-Hosted VS Code: code-server as the Missing Piece of Your Homelab Dev Stack"
date: 2026-11-27
description: "code-server puts a full VS Code in your browser, served from your own hardware. But the real story isn't the editor — it's gluing it to a self-hosted Git server, a local AI coding assistant, and a WireGuard tunnel to build a complete remote dev environment with zero SaaS dependencies. Here's how the pieces fit together and why this might be the most underrated upgrade in a homelab."
tags: ["self-hosted", "vscode", "code-server", "git", "homelab", "devops", "ai", "wireguard", "remote-development", "coder"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-27-self-hosted-vscode-code-server"
---

There's a question that shows up in search a lot more than you'd expect, given how unglamorous it is: *"vscode server self hosted."* And right behind it, its sibling: *"self hosted code server."* Tens of thousands of developers type some version of this every month, and the reason is simple — they've realized something that a lot of us arrive at slowly.

Your editor is the last SaaS-shaped thing left in your development stack.

Think about it. You've already pulled your [Git](/blog/2026-08-18-self-hosted-git-gitea-forgejo-gitlab) off GitHub. You're running a [local AI coding assistant](/blog/2026-06-16-self-hosted-ai-coding-assistants) so your code never leaves the building. You've got a [WireGuard tunnel](/blog/2026-04-21-wireguard-pihole-privacy-stack) so you can reach home from anywhere. And yet, when you want to actually *write code* from a laptop at a coffee shop, you're still syncing files to a machine that runs an editor that lives, conceptually at least, in the cloud.

That's the gap. [code-server](https://github.com/coder/code-server) is the piece that closes it. And what makes it genuinely interesting in 2026 isn't that it's a browser-based VS Code — that's old news. It's that, combined with the rest of your homelab, it stops being "VS Code in a browser" and starts being a *complete remote development environment with zero SaaS*. This post is about the second thing.

## What code-server Actually Is

Let me clear up the framing first, because the name undersells it.

code-server is an open-source project from [Coder](https://coder.com) that runs a full instance of VS Code on a server and serves the UI to your browser. It's not a re-implementation, not a web-based "lookalike." It's the actual VS Code editor — the same one you install locally — running headless and streamed over HTTP. You get the real editor, the real extensions, the real terminal, the real debugger, all in a browser tab.

Why would you want that? A few reasons, and they compound:

- **Your code and your compute stay together.** The editor runs *where the code lives*, so there's no sync step, no "works on my machine," no drift between what's checked out on your workstation and what's on the server.
- **Your machine becomes thin.** A Chromebook, an iPad, a borrowed laptop, a cheap laptop — anything with a browser is now a full dev workstation. The heavy lifting happens on your homelab hardware.
- **You get a persistent environment.** Close the laptop, the editor keeps running. Reopen the browser anywhere, and you're exactly where you left off — same terminal session, same open files, same unsaved state.
- **It's genuinely yours.** No account, no telemetry, no usage caps, no "you've reached your free tier" nag. It's your hardware running your editor.

The trade-off is that it's not a perfect 1:1 with desktop VS Code. A handful of extensions that rely on local desktop APIs — some remote-specific or GPU-heavy ones — don't behave identically. And it's single-user-per-instance by default; it's not a multi-tenant remote dev platform out of the box (that's what Coder's commercial offering does). For a solo developer or a small homelab, those are non-issues. For a team, they're the reason the commercial product exists.

But here's the thing I want to spend the rest of this on: **code-server alone is fine. code-server as one node in a self-hosted dev stack is where it gets powerful.**

## The "Missing Piece" Angle: It's Not the Editor, It's the Glue

Most write-ups of code-server treat it as a toy or a novelty — "look, VS Code in a browser!" — and stop there. The people searching "self hosted code server" are usually asking something more specific, whether they know it or not: *can I replace my entire SaaS dev workflow with things I run myself?*

The answer is yes, and code-server is the keystone. Here's the full picture.

### 1. Self-hosted Git: Gitea or Forgejo

If your editor runs on your homelab, your code should live there too. I wrote at length about [self-hosted Git](/blog/2026-08-18-self-hosted-git-gitea-forgejo-gitlab) recently, so I won't re-litigate the whole thing — the short version is that Forgejo (or Gitea) gives you a lightweight, GitHub-compatible code host that runs on a Raspberry Pi.

The reason it matters here is the *proximity*. With code-server running on the same box (or same network) as your Forgejo instance, the round trip is local. Git operations are instant. Clones, pushes, pulls — all sub-second, no internet latency, no dependency on GitHub's availability. And because both are on your hardware, a GitHub outage is now somebody else's problem, not yours.

The setup is trivially close. Both code-server and Forgejo run as Docker containers, often on the same host or the same LXC. Wire them together and you've got the backbone of a remote dev environment: an editor and a source-of-truth that never leave your house.

### 2. Self-hosted AI assistant: local LLMs in the editor

This is where the "zero SaaS" story gets interesting. The single biggest reason most developers still reach for a cloud editor or a cloud Copilot is the AI. And until recently, running a useful coding model locally was a heavy lift. It isn't anymore.

I covered the landscape in [my guide to self-hosted AI coding assistants](/blog/2026-06-16-self-hosted-ai-coding-assistants), but the relevant point for code-server is this: there are now mature VS Code extensions that talk to a local model instead of a cloud API. You run [Ollama](https://ollama.com) (or a similar local inference server) on your homelab, point a Continue-style extension at it, and you've got code completion and chat that never leave your network.

The magic of doing this *inside code-server* is that the model and the editor live on the same hardware. A decent GPU — even a mid-tier one, or a beefy Mac mini like the one I use for [local LLMs](/blog/2026-06-12-local-llms-mac-mini-practical-guide) — gives you sub-second completions with no per-token billing, no usage caps, and no code egress. Your private repos stay private *by construction*, because the model that's reading them is physically in the room.

This is the piece that makes the whole stack feel like a coherent system rather than a grab bag. Editor, code, and AI all on one network, all owned by you.

### 3. WireGuard or a VPN: reach it from anywhere

The obvious objection to all of this is: *great, but I want to code from a coffee shop, not my basement.* That's where the tunnel comes in.

The two approaches are:

- **A VPN like WireGuard.** This is the gold standard. You run WireGuard on your homelab, and every device you own is a peer. When you're remote, you connect the tunnel and hit `https://code-server.lan` exactly as if you were home. It's the most secure option because nothing is exposed to the public internet at all — the only way in is through the tunnel, which requires your private keys.
- **A reverse tunnel like Cloudflare Tunnel.** I've [written about these](/blog/2026-07-26-cloudflare-tunnels-homelab-guide) before. They let you expose a service through Cloudflare's edge without opening a port, and they layer access policies and SSO on top. The trade-off is that you're routing through a third party, which is philosophically at odds with the "zero SaaS" goal — but it's a legitimate middle ground if you don't want to manage keys on every device.

For a truly "zero SaaS" remote dev environment, WireGuard is the answer. It's not SaaS, it's just a protocol. Combine it with your [self-hosted SSO](/blog/2026-08-08-self-hosted-auth-sso-showdown) and you've got a remote dev stack where the only third party in the loop is your ISP.

### Putting it together

The full picture looks like this:

- **code-server** — the editor, running on your homelab, reachable from any browser
- **Forgejo/Gitea** — the code host, on the same network
- **Ollama + a local model** — the AI assistant, also on the same network
- **WireGuard** — the tunnel that makes the whole thing reachable from anywhere, without exposing a single port

That's not "VS Code in a browser." That's a *development environment*. One where you own the editor, the code, the AI, and the network path. It's the natural endgame of the self-hosting arc this site has been documenting — and code-server is the piece that was always missing from it.

## The Setup

Let me give you the actual recipe, because this is the kind of thing where the theory is obvious but the wiring is where people stall.

### code-server in Docker

The canonical way to run code-server is a single container:

```yaml
# docker-compose.yml
services:
  code-server:
    image: codercom/code-server:latest
    container_name: code-server
    restart: unless-stopped
    environment:
      - PASSWORD=your-strong-password
      - PUID=1000
      - PGID=1000
    volumes:
      - ./code-server-config:/home/coder/.config
      - ./projects:/home/coder/projects
    ports:
      - "8080:8080"
```

`docker compose up -d`, then hit `http://your-server:8080`. You'll be asked for the password you set, and you're dropped into a full VS Code.

A few notes from experience:

- **Don't expose port 8080 to the internet directly.** Bind it to your WireGuard interface or put it behind a reverse proxy with auth. code-server has password auth built in, but it's one password and no brute-force protection on its own. Treat it like the internal service it is.
- **Use `PUID`/`PGID`** so files written by code-server are owned by your normal user, not a container user you'll fight with later.
- **Persist `/home/coder`** (config, extensions, and your code) or you'll lose your environment on every container recreation. The volume above splits it sensibly.

### Wire it to Forgejo

Inside code-server, open the terminal and treat it like any machine:

```bash
git config --global user.name "Bryan Moon"
git config --global user.email "you@example.com"
```

Then clone from your Forgejo instance. If Forgejo is on the same Docker network, the clone URL can just be `http://forgejo:3000/you/repo.git` — no public DNS needed. Generate an SSH key or a token inside code-server and add it to Forgejo, and pushes work exactly like they do anywhere else.

### Point an AI extension at a local model

Install a Continue-style extension in code-server's extension marketplace, then point it at your Ollama endpoint. If Ollama runs on the same host, the base URL is just `http://host.docker.internal:11434` (or the container name if it's on the same network). Pick a model your hardware can handle — I've had good results with the mid-size open models on modest hardware — and you've got completion and chat that never leave the box.

### Make it reachable over WireGuard

Configure WireGuard so your homelab is a peer, then access code-server via its internal address (`http://code-server.lan` or similar). If you want TLS (you should, even over a tunnel), put a reverse proxy like Caddy or Traefik in front with a self-signed or internal CA cert. The specifics are beyond this post's scope, but the [WireGuard guide](/blog/2026-04-21-wireguard-pihole-privacy-stack) I linked earlier covers the tunnel, and any reverse proxy will handle the TLS.

## Is It Actually Worth It?

Let me be honest about the friction, because I don't want to oversell this.

code-server is not a drop-in replacement for desktop VS Code in every scenario. If you do mobile development, or GPU-heavy work, or you rely on specific desktop integrations, you'll hit rough edges. Some extensions misbehave. The browser has minor latency quirks that a native editor doesn't. And there's real setup cost in getting the VPN, the TLS, and the auth right.

But here's what tips the scale for me: **the alternative is silently worse in ways that don't show up in a feature comparison.** Your code egresses to a cloud AI provider. Your repos live on a platform with its own outage schedule and its own corporate incentives. Your environment is scattered across a half-dozen SaaS products, each of which can change its terms or pricing at any moment.

code-server, glued to self-hosted Git, a local model, and a WireGuard tunnel, collapses all of that into *one thing you own*. It's not the flashiest piece of the homelab. It's not the one that gets the "wow" in a screenshot. But it's the piece that turns a collection of self-hosted services into an actual, usable, *complete* development environment — and that's a bigger deal than it gets credit for.

The search demand is there for a reason. People typing "self hosted code server" aren't looking for a novelty. They're looking for the last piece of a stack they've been quietly assembling. This is it.

---

*Are you running code-server, or still on the fence about the whole browser-editor thing? I'm curious whether the AI-assistant angle or the Git-proximity angle is what pushes you over — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [self-hosted Git](/blog/2026-08-18-self-hosted-git-gitea-forgejo-gitlab), [self-hosted AI coding assistants](/blog/2026-06-16-self-hosted-ai-coding-assistants), and [WireGuard + Pi-hole](/blog/2026-04-21-wireguard-pihole-privacy-stack).*
