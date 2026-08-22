---
layout: post.njk
title: "De-Cloudflare: The Self-Hosted Trust Runbook (Audit, Migrate, Verify)"
date: 2026-08-22
description: "The 'Cloudflare silently injects analytics' signal is still climbing, and 'self-hosted trust' is the biggest story in the homelab space right now. Yesterday I published the audit. Today: the actual runbook — concrete configs, copy-paste commands, and a verification checklist to move your request path off Cloudflare and back under your control."
tags: ["cloudflare", "de-cloudflare", "self-hosted", "security", "privacy", "trust", "dns", "tunnels", "workers", "analytics", "homelab", "networking", "caddy", "tailscale", "desec"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust"
---

Yesterday I published [the Cloudflare trust audit](/blog/2026-08-21-audit-cloudflare-dependency/) — the inventory of every silent dependency, the analytics-injection problem, and the decision framework for whether to stay or go.

This is the follow-up. The audit tells you *what* you're depending on. This post tells you *how to actually move off it* — with real configs, copy-paste commands, and a verification checklist you can run at the end to prove the request path is yours again.

If you read the audit and decided "I want my self-hosted claim to actually mean something," this is the runbook.

---

## The One-Sentence Version

**Move DNS off Cloudflare first, replace the CDN/DDoS/TLS layer with Caddy, swap Tunnels for Tailscale or a self-hosted relay, migrate Workers/Pages to a host you control, and kill the analytics beacon — then verify with `dig`, `curl`, and your browser's network tab that no request touches Cloudflare's edge.**

That's the whole thing. The rest of this post is the detail.

---

## Before You Start: Snapshot Your Current State

You can't verify a migration if you don't know where you started. Capture this first.

```bash
# 1. Where do your nameservers point?
dig +short NS yourdomain.com

# 2. What IP does your apex resolve to? (Cloudflare proxy = 104.x / 172.6x.x)
dig +short yourdomain.com

# 3. What's your current TLS cert issuer?
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -issuer

# 4. Are you running cloudflared?
ps aux | grep -i cloudflared
docker ps | grep -i cloudflared

# 5. Do you have Workers/Pages?
npx wrangler whoami 2>/dev/null
npx wrangler pages project list 2>/dev/null
```

Save the output. You'll diff against it at the end.

---

## Phase 1: Move DNS Off Cloudflare

DNS is the foundation, and it's the switch that actually cuts over. Do it **last** in terms of *cutover*, but **first** in terms of *setup* — you want the new DNS provider fully configured and ready before you flip nameservers.

### Pick a DNS provider that doesn't sit in your request path

| Provider | Why | Cost |
|----------|-----|------|
| **deSEC** | Free, open-source-friendly, no tracking, API-first | Free |
| **Porkbun DNS** | Registrar + DNS, clean UI, no proxy layer | Free with domain |
| **Namecheap FreeDNS** | Registrar + DNS, simple | Free with domain |
| **Self-hosted (PowerDNS/BIND)** | Maximum control, maximum work | Your infra |

For most self-hosters, **deSEC** is the sweet spot: it's free, it has a clean API (great for automation), and it does exactly one thing — serve DNS records — without trying to be a CDN, a WAF, or an analytics platform.

### Set up your records at the new provider

Export your current records from Cloudflare (Dashboard → DNS → Export), then recreate them at the new provider. The key difference: **there is no "proxy" toggle anymore.** Every record points directly at your origin.

```bash
# Example: deSEC API — create an A record pointing at your origin IP
curl -X POST https://desec.io/api/v1/domains/yourdomain.com/rrsets/ \
  -H "Authorization: Token $DESEC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"subname": "", "type": "A", "ttl": 3600, "records": ["203.0.113.10"]},
    {"subname": "www", "type": "CNAME", "ttl": 3600, "records": ["yourdomain.com."]}
  ]'
```

### Flip the nameservers

At your **registrar** (not Cloudflare), change the nameservers to your new provider's. Then wait.

```bash
# Watch propagation
watch -n 30 'dig +short NS yourdomain.com'
```

Propagation is usually minutes to a few hours, but TTLs can stretch it to 48. Don't panic if it's not instant.

**Critical ordering note:** flip nameservers *after* your origin is ready to serve traffic directly (Phase 2). Otherwise you'll have a window where your domain points at an origin that isn't listening.

---

## Phase 2: Replace the CDN / DDoS / TLS Layer with Caddy

Once DNS points directly at your origin, *you* are the edge. That means you need to handle TLS, and you probably want a reverse proxy. **Caddy** does both with almost zero config.

### Why Caddy

- **Automatic HTTPS** — Let's Encrypt certs with zero manual steps
- **Automatic HTTP→HTTPS redirect**
- **A sane config file** (Caddyfile) instead of Nginx's sprawl
- **Built-in rate limiting** for basic abuse protection

### Install and configure

```bash
# Install Caddy (Debian/Ubuntu)
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

```caddyfile
# /etc/caddy/Caddyfile
yourdomain.com {
    reverse_proxy localhost:8080

    # Basic rate limiting (replaces a chunk of what Cloudflare's WAF did)
    rate_limit {
        zone dynamic {
            key {remote_host}
            events 100
            window 1m
        }
    }

    # Security headers Cloudflare used to add for you
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

```bash
sudo systemctl enable --now caddy
```

### The honest DDoS caveat

Cloudflare's real DDoS protection is genuinely hard to replicate. But for a homelab or a small personal site, the threat model is different: you're not a target of 100 Gbps volumetric attacks. What you'll actually see is script-kiddie scanning and credential stuffing, and **Caddy's rate limiting + fail2ban + a firewall handles that fine.**

```bash
# fail2ban for SSH and web abuse
sudo apt install fail2ban
sudo systemctl enable --now fail2ban
```

If you *are* a real DDoS target, keep Cloudflare for that one public site and de-Cloudflare everything else. The goal isn't purity — it's *conscious* dependency.

---

## Phase 3: Replace Tunnels

Cloudflare Tunnels are the hardest thing to give up because they're genuinely convenient: no open ports, no dynamic DNS, no reverse proxy. Here are the real alternatives, ranked by how close they get.

| Alternative | Outbound-only? | Third party? | Setup effort |
|-------------|----------------|--------------|--------------|
| **Tailscale Funnel** | Yes | Tailscale (but peer-to-peer, no traffic inspection) | Low |
| **WireGuard + Caddy** | No (VPN inbound) | None | Medium |
| **frp / rathole** (self-hosted relay on a VPS) | Yes | None (you own the VPS) | Medium |
| **Direct port forward + Caddy** | No | None | Low |

### Option A: Tailscale Funnel (closest drop-in)

If you're already on Tailscale, Funnel is the fastest path — it exposes a service to the public internet over your tailnet, outbound-only, no open ports.

```bash
# Expose a service on your tailnet to the public internet
tailscale funnel 8080
```

The tradeoff: Funnel is limited to your tailnet's nodes, and Tailscale is still a third party (though their model is peer-to-peer encryption, not a traffic-inspecting edge).

### Option B: Self-hosted relay with rathole (full control)

If you want the "no open ports" property *and* zero third party, run your own relay on a cheap VPS.

```bash
# On your VPS (the relay)
rathole --server 0.0.0.0:2333

# On your homelab (the client) — forward your service to the VPS
rathole --client your-vps-ip:2333 --service 8080
```

You own the relay, you control the traffic, and your home IP stays hidden. The cost is a $5 VPS and a bit of config.

### Option C: Just open the port (and own it)

For a lot of self-hosters, the simplest honest answer is: **open 443, point Caddy at it, and accept that your IP is public.** Your IP being public isn't a security hole — a misconfigured service is. Caddy + fail2ban + a firewall is a perfectly reasonable "edge" for a personal stack.

---

## Phase 4: Migrate Workers & Pages

This is the deep lock-in. If your code runs on Cloudflare's platform, you can't just repoint DNS — you have to move the code.

### Pages → any static host you control

```bash
# If you're on Pages, your site is static. Move it to:
# 1. Your own server with Caddy (full control)
# 2. GitHub Pages / Netlify / Vercel (still a third party, but not in your request path the same way)
# 3. A $5 VPS running Caddy

# Example: build and serve locally
npx eleventy
sudo cp -r _site/* /var/www/yourdomain.com/
```

### Workers → a small VPS or a serverless runtime you control

A Cloudflare Worker is just a function. The equivalent is:

- **A small VPS running your function** (Node, Bun, Deno) behind Caddy
- **A self-hosted serverless runtime** (OpenFaaS, Knative, or just a cron + webhook)
- **A container on your existing homelab** exposed via Caddy

### KV / D1 / R2 → storage you control

| Cloudflare | Replacement |
|------------|-------------|
| Workers KV | Redis, or a Postgres table |
| D1 (SQLite) | SQLite on your server, or Postgres |
| R2 (object storage) | MinIO (self-hosted S3), or any S3-compatible store |

This is a real migration, not a config change. Budget a weekend for it, and do it *before* you flip DNS so you're not scrambling.

---

## Phase 5: Kill the Analytics Beacon

Even if you stay on Cloudflare for other reasons, this one is non-negotiable.

1. Cloudflare dashboard → **Analytics & Logs** → **Web Analytics**
2. Disable the site (or delete the beacon)
3. Verify the `cloudflareinsights.com` request is gone

And replace it with analytics you actually control — [self-host Umami or Plausible](/blog/2026-08-10-self-hosted-web-analytics-2026/). That's the whole point of that post, and it's the natural companion to this one.

---

## The Verification Checklist

This is the part most people skip. Don't. Run every one of these after the migration and confirm the request path is yours.

```bash
# 1. Nameservers are NOT Cloudflare
dig +short NS yourdomain.com
# ✅ Expect: your new provider (desec.io, porkbun, etc.)
# ❌ Fail: *.ns.cloudflare.com

# 2. Apex resolves to YOUR origin IP, not Cloudflare's
dig +short yourdomain.com
# ✅ Expect: your server's real IP
# ❌ Fail: 104.x.x.x or 172.6x.x.x

# 3. TLS cert is issued by Let's Encrypt (or your CA), not Cloudflare
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -issuer
# ✅ Expect: Let's Encrypt / R3 / E1
# ❌ Fail: Cloudflare, Inc.

# 4. No cloudflared processes remain
ps aux | grep -i cloudflared
docker ps | grep -i cloudflared
# ✅ Expect: no output

# 5. No Workers/Pages projects remain
npx wrangler pages project list
# ✅ Expect: empty

# 6. The analytics beacon is gone (browser)
# Open your site → DevTools → Network → filter "cloudflare"
# ✅ Expect: zero requests to cloudflareinsights.com or /cdn-cgi/
```

Then do the human check: load your site in a private window, click around, and confirm everything works. A migration that "succeeds" on paper but breaks your site is a failed migration.

---

## What You Actually Gain

Let me be concrete about the payoff, because "trust" can feel abstract.

1. **Your request path is yours.** No third party sees, logs, or can modify your traffic. TLS happens on your box. Analytics fire only if *you* add them.
2. **Your "self-hosted" claim is true.** You're not self-hosting the easy parts and outsourcing the hard part. You own the whole path.
3. **No silent surprises.** The analytics-injection signal was a reminder that a third party in your path can change behavior without asking you. Remove the third party, remove the surprise.
4. **You understand your own stack.** The audit + migration forces you to actually know what every layer does. That knowledge is worth more than any single tool.

The cost is real too — more setup, more maintenance, and you lose Cloudflare's genuinely good DDoS protection. I'm not pretending otherwise. But for most self-hosters, the trade is worth it, because **the thing you were trying to build by self-hosting in the first place was control — and you can't outsource control to a third party and still call it control.**

---

## The Bottom Line

The audit (yesterday) told you what you're depending on. This runbook tells you how to stop depending on it.

The order matters: **DNS setup first, origin ready second, nameserver flip third, then tunnels, then Workers/Pages, then the beacon — and verify at every step.** The verification checklist is not optional; it's the difference between "I think I moved off Cloudflare" and "I can prove it."

Start with `dig +short NS yourdomain.com`. If it still says `ns.cloudflare.com`, you know exactly where to begin.

---

*This is the second of two posts on the Cloudflare trust signal. Read the [audit](/blog/2026-08-21-audit-cloudflare-dependency/) for the full inventory and decision framework, and the [self-hosted analytics comparison](/blog/2026-08-10-self-hosted-web-analytics-2026/) for what to replace the beacon with.*

**Related Reading:**
- [The Cloudflare Trust Audit: How to Find Every Silent Dependency and Move Off It](/blog/2026-08-21-audit-cloudflare-dependency/)
- [Cloudflare Tunnels: Expose Your Homelab Without Opening a Single Port](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/)
- [Self-Hosted Web Analytics in 2026: Ditch Google Analytics for Good](/blog/2026-08-10-self-hosted-web-analytics-2026/)
- [WireGuard + Pi-hole: The Privacy Stack That Replaces Your ISP's DNS](/blog/2026-04-21-wireguard-pihole-privacy-stack/)
