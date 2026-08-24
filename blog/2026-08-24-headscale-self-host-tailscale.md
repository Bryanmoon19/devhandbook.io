---
layout: post.njk
title: "Headscale: Self-Host Your Own Tailscale Control Plane"
date: 2026-08-24
description: "Tailscale is the best mesh VPN ever built — but its coordination server is a closed, third-party dependency. Headscale is the open-source reimplementation that puts the control plane back in your hands. Here's how to run it, why DERP nodes matter, and how to migrate your existing clients without re-authenticating."
tags: ["headscale", "tailscale", "wireguard", "vpn", "self-hosted", "de-cloudflare", "networking", "homelab", "derp", "mesh", "privacy", "trust"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-24-headscale-self-host-tailscale"
affiliate: true
cta: true
---

There's a pattern in this de-Cloudflare series, and it's worth naming out loud: **the best tools are often the ones with the most invisible third-party dependency.**

Cloudflare Tunnels are brilliant — until you realize the request path is owned by someone else. Cloudflare DNS is fast — until you realize it's silently injecting analytics. And Tailscale? Tailscale is the best mesh VPN ever built, and its coordination server is a closed, proprietary service you don't control.

That last one is the one people keep asking me about. The Hacker News threads on Tailscale always circle back to the same two questions: *"Can I run my own DERP relay?"* and *"If I self-host the control plane, do I have to re-authenticate every device?"*

The answer to both is **Headscale** — an open-source reimplementation of the Tailscale control server. It's the natural next chapter in this series, because it's the same story as Cloudflare: the *client* is open and excellent, but the *coordination layer* is a black box. Headscale opens the box.

Here's everything I learned running it.

---

## The Problem: Tailscale's Invisible Dependency

Let me be precise about what Tailscale actually is, because the mental model matters.

Tailscale is two things:

1. **The client** (`tailscaled`) — a WireGuard-based mesh VPN agent that runs on every device. It's open source, and it's genuinely excellent. NAT traversal, automatic key rotation, magic DNS, subnet routing — all of it lives here.

2. **The coordination server** — the thing that tells your devices about each other. It distributes public keys, coordinates NAT traversal, and manages the ACLs that decide who can talk to whom. This is the part Tailscale runs for you, and it's **not** open source.

When you run `tailscale up`, your device authenticates to Tailscale's coordination server (or your SSO provider via Tailscale). That server is the single point of trust in the whole system. It knows every device, every key, every ACL rule. If it goes down, your existing connections keep working (WireGuard is peer-to-peer), but you can't add devices, rotate keys, or change policy.

For most people, that's fine. Tailscale's free tier is generous, and the service is well-run. But if you've been following this series, you already know the objection: **you're outsourcing the trust layer of your own network to a third party.**

That's exactly what Headscale fixes.

---

## What Headscale Is (And Isn't)

[Headscale](https://github.com/juanfont/headscale) is an open-source, self-hosted reimplementation of the Tailscale control server. It speaks the same protocol, so you keep using the **official Tailscale clients** — you just point them at your own server instead of Tailscale's.

Here's the key insight that makes Headscale so compelling: **you don't give up the good parts of Tailscale.** The client, the NAT traversal, the WireGuard data plane, the magic DNS — all of it still works. You're only replacing the coordination layer, which is precisely the part that was closed.

What you get in return:

- **Full control of the trust layer.** Your keys, your ACLs, your device inventory live on your hardware.
- **No third-party account.** No Tailscale login, no SSO dependency, no "what happens if Tailscale gets acquired" question.
- **Self-hosted DERP relays.** More on this below — it's the part HN keeps asking about.
- **Unlimited devices and users.** No free-tier caps, no per-user pricing.

What you *don't* get:

- **The Tailscale admin dashboard.** Headscale has a CLI and a basic web UI, but it's not the polished Tailscale console.
- **Tailscale's managed DERP network.** You run your own relays (or use the public ones, which is a nuance we'll get to).
- **Hand-holding.** Headscale assumes you're comfortable with a config file and a CLI.

The trade is honest: you give up polish and convenience, you gain sovereignty. For a homelab, that's usually the right trade.

---

## Headscale vs Tailscale: The Honest Comparison

| | Tailscale (managed) | Headscale (self-hosted) |
|---|---|---|
| Control plane | Tailscale's servers | Your server |
| Client | Official `tailscaled` | Official `tailscaled` (same) |
| Data plane | WireGuard P2P | WireGuard P2P (same) |
| NAT traversal | Yes | Yes (same client) |
| Magic DNS | Yes | Yes |
| ACLs | Tailscale policy syntax | Same syntax, self-managed |
| DERP relays | Tailscale's global network | Self-hosted (or public) |
| Admin UI | Polished web console | CLI + minimal web UI |
| Device limits | Free tier caps | Unlimited |
| Third-party trust | Tailscale + your SSO | None (you own it) |
| Maintenance | Zero | You patch and monitor it |

The headline: **the networking is identical, because it's the same client.** The only thing that changes is who runs the coordination server. That's a smaller change than most people expect, and it's why migrating is less scary than it sounds.

---

## The DERP Question (The HN Hot Topic)

Every Tailscale thread eventually hits DERP, and it's the most misunderstood part of the whole system. Let me clear it up, because it's the difference between "Headscale works" and "Headscale works *well*."

**DERP** (Detour Encrypted Routing Protocol) is Tailscale's relay network. Here's the thing most people don't realize: **WireGuard is peer-to-peer, but it can't always establish a direct connection.** When two devices are behind symmetric NATs, or on networks that block UDP, the direct path fails. That's when Tailscale falls back to routing traffic through a DERP relay.

So DERP is the *fallback*, not the primary path. But it's a critical fallback, because without it, some device pairs simply can't connect at all.

Here's the nuance that trips people up with Headscale:

- **By default, Headscale uses Tailscale's public DERP servers.** That's convenient, but it means your *fallback* traffic still transits Tailscale's infrastructure. If your goal is full de-Cloudflare-style sovereignty, that's a leak.
- **You can run your own DERP server** (`derper`), and Headscale makes it easy. This is the "self-host your DERP" answer HN keeps looking for.

The honest recommendation: **run your own DERP relay.** It's a single Go binary, it's low-traffic (it only carries fallback traffic), and it closes the last hole in the "I control my own network" story. I'll show you how below.

One more DERP nuance worth knowing: DERP relays are **not** where your traffic's confidentiality lives. WireGuard encrypts end-to-end regardless of path, so a DERP relay sees only encrypted packets. The concern with using Tailscale's public DERP isn't *privacy of content* — it's *dependency and metadata*. A relay knows which of your nodes are talking, when, and how much. If you care about that metadata, self-host the relay.

---

## Migrating Clients Without Re-Auth (The Other HN Question)

The second question that always comes up: *"If I move from Tailscale to Headscale, do I have to re-authenticate every device?"*

The short answer is **no — but you do have to re-register them.** Let me be precise, because "re-auth" and "re-register" are different things and the distinction matters.

- **Re-authenticating** means logging back into an SSO provider, re-approving OAuth scopes, re-entering credentials. You don't have to do any of that with Headscale, because Headscale doesn't use SSO at all — it uses pre-shared keys and its own node registration.
- **Re-registering** means telling your new control server "this device belongs to me now." You *do* have to do this, because your devices are currently registered to Tailscale's server, and Headscale is a different server.

The good news: **re-registration is fast and scriptable.** It's not the painful "re-auth every device" experience people fear. Here's the actual migration flow:

1. Stand up Headscale and create a pre-auth key.
2. On each device, log out of Tailscale (`tailscale logout`) and log into your Headscale server (`tailscale up --login-server https://your-headscale.example.com`).
3. Approve the node in Headscale (`headscale nodes list` then `headscale nodes register`).

That's it. No SSO, no OAuth, no credential re-entry. For a homelab with a dozen devices, the whole migration is an afternoon. For a single laptop, it's five minutes.

The one thing to plan for: **your ACLs and DNS settings don't migrate automatically.** Tailscale's ACLs live in their admin console; Headscale's live in a `config.yaml` on your server. You'll need to recreate them. It's not hard — the syntax is the same — but it's the one piece of manual work in the migration.

---

## Setting Up Headscale (The Fast Path)

Here's the concrete path I recommend. I'll assume Docker, since that's what most homelabs run, but Headscale is a single Go binary if you prefer bare metal.

### 1. Create the config

```bash
mkdir -p ~/headscale && cd ~/headscale

# Generate a minimal config
docker run --rm -v $PWD:/etc/headscale \
  headscale/headscale:latest headscale config > config.yaml
```

The generated `config.yaml` is well-commented. The settings you actually need to change:

```yaml
server_url: https://headscale.example.com   # your public URL
listen_addr: 0.0.0.0:8080
metrics_listen_addr: 0.0.0.0:9090

# Where node data lives
db_type: sqlite
db_path: /var/lib/headscale/db.sqlite

# Magic DNS
dns_config:
  base_domain: example.com
  magic_dns: true
  domains: []
  nameservers:
    - 1.1.1.1
```

### 2. Run it

```bash
docker run -d \
  --name headscale \
  -v $PWD/config.yaml:/etc/headscale/config.yaml \
  -v $PWD/data:/var/lib/headscale \
  -p 8080:8080 \
  --restart unless-stopped \
  headscale/headscale:latest headscale serve
```

### 3. Create a namespace and pre-auth key

```bash
# Create a user (Headscale calls them "users" now, formerly "namespaces")
docker exec headscale headscale users create myuser

# Generate a pre-auth key (valid 1 hour by default)
docker exec headscale headscale preauthkeys create --user myuser
```

### 4. Point a client at it

```bash
# On any device with the Tailscale client installed:
tailscale up --login-server https://headscale.example.com --authkey <PREAUTH_KEY>
```

### 5. Register the node

```bash
docker exec headscale headscale nodes list
docker exec headscale headscale nodes register --user myuser <NODE_NAME>
```

That's the whole thing. One container, one config file, and your devices are talking to *your* coordination server instead of Tailscale's.

---

## Self-Hosting Your DERP Relay

Now the part HN keeps asking about. Running your own DERP relay closes the last dependency on Tailscale's infrastructure.

The relay is a separate binary called `derper` (it ships in the Tailscale repo). Here's the minimal setup:

```bash
# Run derper on a public VPS (it needs a public IP + TLS)
docker run -d \
  --name derper \
  -p 443:443 \
  -p 3478:3478/udp \
  --restart unless-stopped \
  ghcr.io/tailscale/derper:latest \
  derper --hostname derp.example.com --certmode letsencrypt
```

Then tell Headscale about it in `config.yaml`:

```yaml
derp:
  server:
    enabled: true
    stun_listen_addr: "0.0.0.0:3478"
  urls: []
  paths: []
  auto_update_enabled: true
  update_frequency: 24h
```

And add your relay to the DERP map so clients know about it:

```yaml
derp:
  urls:
    - https://controlplane.tailscale.com/derpmap/default
  paths:
    - /etc/headscale/derp.yaml
```

Your `derp.yaml` points at your own relay:

```yaml
regions:
  900:
    regionid: 900
    regioncode: "selfhosted"
    regionname: "My DERP"
    nodes:
      - name: "900a"
        regionid: 900
        hostname: "derp.example.com"
        stunport: 3478
        stunonly: false
```

A few honest caveats about self-hosting DERP:

- **You need a public IP and TLS.** DERP relays sit on the public internet, so this is a VPS job, not a "run it on your home server behind NAT" job. (Your Headscale *control server* can be anywhere, but the DERP relay needs to be reachable.)
- **It's low-traffic.** Remember, DERP only carries fallback traffic when direct WireGuard fails. A $5 VPS is more than enough.
- **Keep one public relay as a backup.** If your self-hosted relay goes down, devices that can't establish direct connections lose connectivity. Pointing at Tailscale's public DERP map as a fallback is a reasonable safety net — just know it's a dependency you're choosing to keep.

---

## Security Hardening

Headscale puts the trust layer in your hands, which means you now own the security of that layer. Here's what I'd do before calling it production-ready:

1. **Put it behind a reverse proxy with TLS.** Headscale's `server_url` must be HTTPS, and the clients will refuse to talk to it over plain HTTP. Caddy or Nginx in front is the standard setup.

2. **Use short-lived pre-auth keys.** The default is 1 hour, which is right. Don't create long-lived keys "for convenience" — that's how you get orphaned nodes.

3. **Expire unused nodes.** `headscale nodes expire <name>` removes a device from the mesh. Do this when you decommission hardware.

4. **Lock down the ACLs.** Headscale uses the same policy syntax as Tailscale. Start with a default-deny policy and open up only what you need:

```yaml
# policy.yaml
acls:
  - action: accept
    src: ["myuser"]
    dst: ["myuser:*"]
```

5. **Back up the SQLite DB.** Your entire network topology, keys, and ACLs live in one file. If you lose it, you're re-registering every device. Back it up like you'd back up any critical database.

6. **Monitor it.** Headscale exposes Prometheus metrics on `:9090`. If you're already running Uptime Kuma or Beszel, add a check.

---

## The Honest Verdict: Should You Switch?

I've spent this whole post telling you how, so let me give you the straight answer.

**Switch to Headscale if:**

1. **You're already de-Cloudflaring.** If you've read the [Cloudflare Trust Audit](/blog/2026-08-21-audit-cloudflare-dependency/) and decided to reduce third-party dependencies, Headscale is the same logic applied to your VPN. It's the most natural next step in this series.

2. **You have more than a handful of devices.** Tailscale's free tier is generous, but if you're running a real homelab — servers, laptops, phones, a NAS, a few VPSes — the caps start to matter, and Headscale has none.

3. **You care about the metadata.** Even if your traffic is encrypted, Tailscale's coordination server knows your device inventory, your connection patterns, and your ACL structure. If that metadata matters to you, self-host.

4. **You want to learn how mesh VPNs actually work.** There's no better way to understand NAT traversal, DERP, and the control-plane/data-plane split than running your own control plane.

**Don't switch if:**

- You have two devices and just want them to talk. Tailscale's free tier is perfect for that, and Headscale is overkill.
- You're not comfortable with a config file and a CLI. Headscale's admin experience is functional, not polished.
- You need Tailscale's managed DERP network for reliability. If you're not willing to run (and monitor) your own relay, you're keeping a dependency anyway.

The honest framing: **Headscale isn't "Tailscale but free." It's "Tailscale but yours."** The networking is identical, the client is identical, and the only thing you're changing is who holds the keys. For a self-hoster, that's the whole point.

---

## The Bottom Line

This series keeps landing on the same lesson, and Headscale is the cleanest example of it yet: **the client is almost never the problem. The coordination layer is.**

Tailscale's client is open, excellent, and worth keeping. Its control server is closed, and that's the part that matters for trust. Headscale lets you keep the good part and replace the part you don't control — with a single Go binary, a single config file, and the same clients you already use.

The two questions HN keeps asking have clean answers: **yes, you can self-host your DERP relay** (and you should, if you want full sovereignty), and **no, you don't have to re-authenticate your devices** (you re-register them, which is fast and scriptable).

If you've been following the de-Cloudflare thread through this series — the [Tunnels guide](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/), the [analytics comparison](/blog/2026-08-10-self-hosted-web-analytics-2026/), the [trust audit](/blog/2026-08-21-audit-cloudflare-dependency/) — Headscale is the logical next move. It's the same principle applied to the one network layer you probably haven't audited yet: your own VPN.

---

*Are you running Headscale? Did you self-host your DERP relay, and did the client migration go as smoothly as I'm claiming? I'd love to hear what worked (and what didn't) — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on the [Cloudflare Trust Audit](/blog/2026-08-21-audit-cloudflare-dependency/) and [WireGuard + Pi-hole for a self-hosted privacy stack](/blog/2026-04-21-wireguard-pihole-privacy-stack/).*
