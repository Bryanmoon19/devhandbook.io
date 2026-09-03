---
layout: post.njk
title: "Cloudflare Tunnel Alternatives: The Self-Hosted Tunnel Stack (Gopher, frp, rathole, boringproxy)"
date: 2026-09-03
description: "You audited your Cloudflare dependency and wrote the de-Cloudflare runbook — but the runbook never told you what to replace Tunnels with. Here's the actual answer: a comparison of Gopher, frp, rathole, and boringproxy on latency, auth, and NAT traversal, with working configs for each, so you can expose your homelab without a third party in the request path."
tags: ["cloudflare", "de-cloudflare", "tunnel", "tunneling", "gopher", "frp", "rathole", "boringproxy", "self-hosted", "homelab", "nat", "reverse-proxy", "networking", "privacy", "trust", "wireguard", "tailscale"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-09-03-self-hosted-tunnel-alternatives-gopher-frp-rathole"
affiliate: true
cta: true
---

The de-Cloudflare series has a hole in it, and I want to close it.

Two weeks ago I published [the audit](/blog/2026-08-21-audit-cloudflare-dependency/) — the inventory of every silent dependency Cloudflare holds over your homelab. Then the [runbook](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/) — the concrete steps to move DNS, TLS, and analytics off their edge. But the runbook has a gap I keep getting asked about: *"You told me to replace Cloudflare Tunnels with 'a self-hosted relay' — but which one?"*

Fair. "A self-hosted relay" is a hand-wave, not an answer. So here's the answer.

This is the post that actually delivers the replacement stack. Four self-hosted tunnel tools — **Gopher**, **frp**, **rathole**, and **boringproxy** — compared on the things that actually matter when you're exposing a homelab: latency, authentication, NAT traversal, and how much of your request path you actually own. With working configs for each, and a clear recommendation at the end.

## Why You Need a Tunnel at All

First, the framing. A tunnel exists to solve one problem: **your services live behind NAT or a firewall, and you want to reach them from the public internet without opening inbound ports.**

Cloudflare Tunnels solved this brilliantly — run a `cloudflared` daemon, it dials *out* to Cloudflare's edge, and Cloudflare routes public traffic back down that outbound connection. No port forwarding, no dynamic DNS, no exposing your home IP. The catch, which the audit covered: **the request path is owned by Cloudflare.** They terminate your TLS, they see your traffic, and they can change behavior without asking you.

A self-hosted tunnel solves the same problem — outbound-only connection, no open ports — but *you* own the relay. The tradeoff is that you now run the relay server yourself, which means you need a VPS or a second machine with a public IP. That's the honest cost, and I'll say it up front: **self-hosting a tunnel means renting a small VPS.** There's no way around needing *some* public endpoint. The question is whether that endpoint is a third party's edge or a $5 box you control.

## The Four Contenders

| Tool | Language | Model | Best For |
|------|----------|-------|----------|
| **Gopher** | Go | Single binary, client + server | The "Cloudflare Tunnel but self-hosted" drop-in |
| **frp** | Go | Client + server, rich config | The battle-tested workhorse with every feature |
| **rathole** | Rust | Client + server, minimal | Raw speed and low resource use |
| **boringproxy** | Go | Server + web UI, auto-TLS | Zero-config HTTPS with a management dashboard |

All four are open source, all four use an outbound-only connection model, and all four are actively maintained in 2026. The differences are in *how much* they do for you and *how fast* they are.

## Gopher — The Cloudflare Tunnel Drop-In

**Gopher** is the newest of the four and the one that most directly answers "I want Cloudflare Tunnels but self-hosted." It's a single Go binary that runs as both a client and a server, and its whole design philosophy is "one command, no config file."

The mental model is almost identical to `cloudflared`:

- You run the **server** on your VPS: `gopher server`
- You run the **client** on your homelab box, pointing at the server, with a list of what to expose: `gopher client --server vps.example.com --tunnel plex:32400`

That's it. The client dials out to the server, the server accepts public traffic and routes it back down the tunnel. No YAML, no TOML, no config sprawl.

**What it's good at:** Simplicity. If you're migrating off Cloudflare Tunnels and want the least-friction path, Gopher is the closest thing to a drop-in replacement. The command-line interface is deliberately minimal, and it handles the common cases (HTTP, TCP, and UDP) without ceremony.

**What it's weaker at:** It's young. The feature surface is smaller than frp's — fewer auth backends, less granular per-tunnel control, and a smaller community to ask when something breaks. For a single user exposing a handful of services, that's fine. For a complex multi-user setup, you may outgrow it.

**The honest tradeoff vs. Cloudflare:** You lose Cloudflare's DDoS protection and their global anycast network. A single VPS is a single point of failure and a single point of attack. You gain a request path that's entirely yours.

## frp — The Battle-Tested Workhorse

**frp** (Fast Reverse Proxy) is the oldest and most widely deployed of the four. If you've been in the self-hosting world for any length of time, you've almost certainly seen an `frpc.ini` / `frpc.toml` file. It's the default answer to "how do I expose a service behind NAT" and has been for years.

frp's model is the same client/server split, but with a much richer config surface:

```toml
# frps.toml — the server, on your VPS
bindPort = 7000
auth.method = "token"
auth.token = "your-long-random-token"

# frpc.toml — the client, on your homelab box
serverAddr = "vps.example.com"
serverPort = 7000
auth.method = "token"
auth.token = "your-long-random-token"

[[proxies]]
name = "plex"
type = "tcp"
localIP = "127.0.0.1"
localPort = 32400
remotePort = 32400
```

**What it's good at:** Everything. frp supports TCP, UDP, HTTP, HTTPS, and a dozen other proxy types. It has built-in auth (token, OIDC, and more), a dashboard, per-proxy bandwidth limits, and a huge community. If you need a feature, frp probably has it.

**What it's weaker at:** The config is verbose, and the sheer number of options can be overwhelming. It's also the heaviest of the four in terms of cognitive load — you're not going to remember the exact TOML keys without the docs open.

**The honest tradeoff:** frp is the safe choice. It's not the fastest, not the simplest, but it's the one that won't surprise you. If you want a tunnel you can set up once and forget about, frp is it.

## rathole — Raw Speed, Minimal Everything

**rathole** is the Rust answer to the same problem, and its pitch is simple: **it's fast, and it's tiny.** The name is a pun — a "rat hole" is a small, hidden passage, and rathole is a small, fast tunnel.

rathole's config is deliberately minimal:

```toml
# server.toml — on your VPS
[server]
bind_addr = "0.0.0.0:2333"

[server.services.plex]
token = "your-long-random-token"
bind_addr = "0.0.0.0:32400"

# client.toml — on your homelab box
[client]
remote_addr = "vps.example.com:2333"

[client.services.plex]
token = "your-long-random-token"
local_addr = "127.0.0.1:32400"
```

**What it's good at:** Performance. rathole is written in Rust, uses a single binary for both roles, and is measurably faster and lighter than frp in most benchmarks. If you're tunneling a high-throughput service — a media server, a file sync, a game server — rathole's lower overhead matters. It also has a clean, minimal config that's easy to reason about.

**What it's weaker at:** Fewer features. No web dashboard, fewer proxy types, and a smaller community. It does TCP and UDP well and not much else. If you need HTTP-specific features like custom domains per service or automatic TLS, you'll be pairing rathole with a reverse proxy in front of it.

**The honest tradeoff:** rathole is the "I care about performance and I'm comfortable with a leaner tool" choice. It's the one I'd pick for a media-heavy homelab where every millisecond of latency and every megabyte of RAM counts.

## boringproxy — Zero-Config HTTPS with a Dashboard

**boringproxy** is the odd one out, and it's worth including because it solves a *different* part of the problem. The other three are raw tunnels — they move bytes, and you handle TLS yourself. boringproxy bundles the tunnel *and* the TLS *and* a web UI for managing it all.

The pitch: run `boringproxy server` on your VPS, open the web dashboard, and add a tunnel. boringproxy automatically provisions Let's Encrypt certificates for each tunnel, so you get HTTPS without touching a reverse proxy or a certbot config.

**What it's good at:** The zero-config HTTPS story. If the thing that's been stopping you from self-hosting a tunnel is "I don't want to deal with TLS certificates," boringproxy removes that objection entirely. The dashboard is also genuinely useful for managing multiple tunnels across multiple machines.

**What it's weaker at:** It's the least "raw" of the four — more moving parts, more opinionated about how you should do things. And because it bundles TLS, it's less flexible if you already have a reverse proxy you like.

**The honest tradeoff:** boringproxy is the "I want the Cloudflare experience — dashboard, auto-HTTPS — but self-hosted" choice. It's the closest to Cloudflare Tunnels in *feel*, even though Gopher is closer in *simplicity*.

## The Decision: Which One Should You Run?

Here's the honest recommendation, because a comparison post that refuses to pick is just a listicle:

- **Migrating off Cloudflare Tunnels and want the least friction?** → **Gopher.** It's the closest to a drop-in replacement, and the single-binary, no-config design means you'll be up in minutes.
- **Want the safe, battle-tested default with every feature?** → **frp.** It's not the fastest or the simplest, but it's the one that won't surprise you, and the community is huge.
- **Tunneling high-throughput media or file traffic and care about speed?** → **rathole.** The Rust implementation is measurably lighter and faster, and the minimal config is a feature, not a bug.
- **Want auto-HTTPS and a management dashboard without extra tooling?** → **boringproxy.** It bundles TLS and a web UI, which removes the two biggest friction points.

My personal setup: **rathole for the media server** (throughput matters) and **frp for everything else** (stability matters). But if I were starting fresh today and migrating off Cloudflare Tunnels, I'd reach for Gopher first and only reach for frp if I hit a feature gap.

## The One Thing All Four Share

Whatever you pick, the security model is the same, and it's the part most people get wrong:

**Your tunnel server is now a public-facing attack surface.** When you self-host a tunnel, you're not just moving bytes — you're running a service that accepts connections from the public internet and routes them into your home network. That's a bigger deal than it sounds.

Three rules, non-negotiable:

1. **Authenticate the tunnel.** Every one of these tools supports a shared token or key between client and server. Use it. An unauthenticated tunnel server is an open door into your network.
2. **Put the server on a VPS, not your home box.** The whole point is that the *public* endpoint is a cheap VPS you can nuke and rebuild, while your *home* network stays behind NAT. Don't defeat the purpose by running the server on your home IP.
3. **Treat the tunnel as a transport, not a security boundary.** The tunnel gets traffic to your service; it doesn't authenticate your users. Put real auth (SSO, basic auth, a reverse proxy with access control) in front of whatever you expose.

## The Bottom Line

The de-Cloudflare series was always building toward this: **you can't just remove a third party from your request path — you have to replace it with something you own.** The audit told you what to remove. The runbook told you how. This post tells you what to put in its place.

Gopher, frp, rathole, and boringproxy are all mature, all open source, and all capable of replacing Cloudflare Tunnels for a homelab. The differences are in simplicity, speed, and how much they do for you — and the honest answer is that any of the four is a real upgrade in *control*, even if it's a downgrade in *convenience*.

That's the trade you're making, and it's the same trade the whole series has been about: **convenience is what you pay a third party for. Control is what you get when you stop.**

---

*This is the third post in the de-Cloudflare series. Read the [audit](/blog/2026-08-21-audit-cloudflare-dependency/) for the full inventory, the [runbook](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/) for the migration steps, and the [Headscale guide](/blog/2026-08-24-headscale-self-host-tailscale/) for the mesh-VPN half of the same story.*

**Related Reading:**
- [The Cloudflare Trust Audit: How to Find Every Silent Dependency and Move Off It](/blog/2026-08-21-audit-cloudflare-dependency/)
- [De-Cloudflare: The Self-Hosted Trust Runbook (Audit, Migrate, Verify)](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/)
- [Headscale: Self-Host Your Own Tailscale Control Plane](/blog/2026-08-24-headscale-self-host-tailscale/)
- [Cloudflare Tunnels: Expose Your Homelab Without Opening a Single Port](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/)
- [WireGuard + Pi-hole: The Privacy Stack That Replaces Your ISP's DNS](/blog/2026-04-21-wireguard-pihole-privacy-stack/)
