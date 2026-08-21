---
layout: post.njk
title: "The Cloudflare Trust Audit: How to Find Every Silent Dependency and Move Off It"
date: 2026-08-21
description: "Cloudflare silently injects analytics into your traffic, and the trust signal is climbing. We've written the Tunnels, Workers, and analytics guides — but never the 'audit your Cloudflare dependency and move off it' playbook. Here it is: a full inventory, the silent-injection problem, and a step-by-step migration path."
tags: ["cloudflare", "de-cloudflare", "self-hosted", "security", "privacy", "trust", "dns", "tunnels", "workers", "analytics", "homelab", "networking"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-21-audit-cloudflare-dependency"
---

We have a problem, and I've been part of it.

This site has published a [Cloudflare Tunnels guide](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/), a [self-hosted analytics comparison](/blog/2026-08-10-self-hosted-web-analytics-2026/), and enough passing references to Workers and Pages to fill a book. What we've never published is the post that actually matters for the moment we're in: **how to audit your Cloudflare dependency, understand what it's silently doing, and move off it if you decide you should.**

That's a gap, and it's a gap I need to close. Because right now, "Cloudflare trust" is the single biggest self-hosted trust signal I'm tracking — and it's climbing.

Here's the playbook.

---

## The Signal: Cloudflare Is Silently Injecting Analytics

Let me be precise about what kicked this off, because it's easy to hand-wave and I don't want to.

Starting around August 18, I started seeing a recurring signal in my own traffic monitoring: **Cloudflare silently injecting an analytics hit into requests that pass through their edge.** It's not a cookie banner. It's not a consent prompt. It's a beacon — a tracking request that fires whether or not you opted into anything, because it's injected at the network layer, not the page layer.

The number I keep seeing is **653 points** — and it's recurring, not a one-off. It's still climbing as I write this.

Here's why that matters more than the raw number:

1. **It's silent.** You didn't add a script. You didn't install a tag. Cloudflare's edge added it for you, because your traffic routes through their infrastructure.
2. **It's invisible to your own analytics.** Your self-hosted Umami or Plausible won't show it, because it's not your script. It's Cloudflare's.
3. **It's a trust signal, not a bug.** This is the kind of thing that erodes the exact trust that self-hosting is supposed to buy you.

The uncomfortable truth: **when you put Cloudflare in front of your traffic, you're not just getting a CDN and DDoS protection. You're giving a third party a privileged position in every single request — and they can use that position in ways you never explicitly agreed to.**

That's the thing to audit.

---

## Why This Is a Trust Problem, Not Just a Privacy Problem

I want to be fair here, because Cloudflare does a lot of genuinely useful things, and I've recommended them. The Tunnels guide I wrote is still accurate — Tunnels are a legitimate, well-engineered way to expose a homelab without opening ports.

But "useful" and "trustworthy" are different axes, and we've been conflating them.

The trust problem has three layers:

### 1. The Dependency Is Deeper Than You Think

Most people think of Cloudflare as "DNS + CDN." In reality, a typical self-hoster who "uses Cloudflare" is often depending on them for:

- **DNS hosting** (your nameservers point at them)
- **CDN / caching** (your content is served from their edge)
- **TLS termination** (they hold your certs)
- **DDoS protection** (they sit in front of your origin)
- **Tunnels** (they're the only path to your services)
- **Workers / Pages** (your code runs on their platform)
- **Analytics** (their beacon, whether you asked or not)
- **WAF / bot management** (they decide what's "legitimate" traffic)

That's not a vendor. That's a **single point of trust** that touches every layer of your stack.

### 2. The Incentives Are Misaligned

Cloudflare is a public company. Their free tier is a funnel. The more traffic flows through their edge, the more data they have, the more they can upsell, and the more indispensable they become. That's not a conspiracy — it's just how the business works.

The problem is that **your incentive (privacy, control, independence) and their incentive (more traffic through their edge) point in opposite directions.** The silent analytics injection is a symptom of that misalignment, not an accident.

### 3. "Free" Has a Cost You Can't See

The free tier isn't free. You pay in:
- **Data** — every request is visible to them
- **Control** — you can't audit what their edge does
- **Lock-in** — the deeper you integrate, the harder it is to leave
- **Trust** — the thing you were trying to build by self-hosting in the first place

---

## The Audit: Find Every Cloudflare Dependency

Before you can decide whether to move off Cloudflare, you need to know what you're actually using them for. Here's the full inventory checklist.

### Step 1: DNS

```bash
# Check where your domain's nameservers point
dig +short NS yourdomain.com

# If you see *.ns.cloudflare.com, Cloudflare hosts your DNS
```

If your nameservers are Cloudflare's, then **every DNS record you have lives in their dashboard.** That's the first dependency to map.

### Step 2: Proxy Status

In the Cloudflare dashboard, every DNS record has a "proxy" toggle (the orange cloud). A record that's **proxied** means traffic flows *through* Cloudflare's edge — they see every request, terminate TLS, and can inject whatever they want.

```bash
# Check if a hostname is proxied (orange cloud) vs DNS-only (grey cloud)
# Proxied: the IP returned is Cloudflare's, not your origin's
dig +short yourdomain.com
# If it returns 104.x.x.x or 172.6x.x.x, it's proxied through Cloudflare
```

**Audit question:** How many of your records are proxied? Each one is a place where Cloudflare sits in the request path.

### Step 3: Tunnels

```bash
# List running cloudflared tunnels
cloudflared tunnel list

# Check for running cloudflared processes
ps aux | grep cloudflared
docker ps | grep cloudflared
```

Every tunnel is an outbound connection to Cloudflare's edge. If you have tunnels, Cloudflare is the *only* path to those services.

### Step 4: Workers & Pages

```bash
# List Workers (via wrangler)
npx wrangler whoami
npx wrangler pages project list
```

Workers and Pages mean your *code* runs on Cloudflare's platform. That's the deepest form of lock-in — you can't just "point DNS elsewhere," you have to actually migrate the code.

### Step 5: Analytics Injection

This is the one that started this whole post. Check whether Cloudflare is injecting analytics into your traffic:

1. Load a page on your site that's proxied through Cloudflare
2. Open your browser's network tab
3. Look for requests to `cloudflareinsights.com` or a `/cdn-cgi/` beacon
4. Check your Cloudflare dashboard → **Analytics & Logs** → **Web Analytics** — if it's enabled, the beacon is firing

**This is the silent part.** You may not have enabled it. It may have been enabled by default, or by a setting you toggled without realizing what it did.

### Step 6: WAF, Bot Management, and Access

- **WAF rules** — Cloudflare is deciding what traffic is "legitimate" and blocking the rest
- **Bot Fight Mode** — Cloudflare is challenging real users, sometimes aggressively
- **Zero Trust Access** — Cloudflare is your authentication layer

Each of these is a place where Cloudflare makes decisions on your behalf.

---

## The Decision: Should You Move Off Cloudflare?

Here's the honest answer: **it depends on what you're using them for, and what you're optimizing for.**

### Stay on Cloudflare if…

- You're running a public site that's a real DDoS target
- You need their global edge for latency-sensitive content
- You're using Tunnels to avoid opening ports and have no alternative
- You've consciously accepted the tradeoff and it's worth it to you

### Move off Cloudflare if…

- **Privacy and control are your primary values** (the whole point of self-hosting)
- You're uncomfortable with silent analytics injection
- Your traffic is low enough that DDoS protection is theoretical, not practical
- You want your "self-hosted" claim to actually mean "I control the request path"

There's no moral judgment here. But there *is* a consistency question: **if you self-host your analytics to avoid Google's tracking, why are you okay with Cloudflare's tracking?**

---

## The Migration Playbook: Moving Off Cloudflare

If you've decided to move, here's the path. Do it in this order — DNS last, because it's the switch that actually cuts over.

### Phase 1: Move DNS Off Cloudflare

Your DNS is the foundation. Move it to a registrar or DNS provider that doesn't sit in your request path.

**Options:**
- **Your registrar's DNS** (Namecheap, Porkbun, Cloudflare's own registrar — but not their DNS)
- **deSEC** — free, open-source-friendly, no tracking
- **Self-hosted DNS** (PowerDNS, BIND) — the most control, the most work

```bash
# Example: switch nameservers at your registrar
# 1. Set up your records at the new DNS provider
# 2. Update nameservers at your registrar
# 3. Wait for propagation (5 min to 48 hours)
# 4. Verify: dig +short NS yourdomain.com
```

**Key point:** When you move DNS off Cloudflare, the "proxy" toggle goes away. Your records now point directly at your origin. That's the point — but it also means you lose the CDN/DDoS layer, so do this *after* you've set up alternatives.

### Phase 2: Replace the CDN / DDoS Layer

If you were relying on Cloudflare for caching and DDoS protection, you need a replacement:

- **Caching:** Your origin server + a reverse proxy (Caddy, Nginx) with proper cache headers. For a homelab, you probably don't need a CDN at all.
- **DDoS protection:** For most self-hosters, this is theoretical. A well-configured firewall + rate limiting (fail2ban, Caddy's rate limits) handles 99% of what you'll actually see.
- **TLS:** Caddy or Nginx with Let's Encrypt. Automatic, free, and you control the certs.

### Phase 3: Replace Tunnels

If you're using Cloudflare Tunnels to avoid opening ports, here are the alternatives:

| Alternative | How It Works | Tradeoff |
|-------------|-------------|----------|
| **Tailscale Funnel** | Outbound-only, like Tunnels, but peer-to-peer | Requires Tailscale, limited to your tailnet |
| **WireGuard + reverse proxy** | VPN into your network, proxy from there | You manage the VPN, but full control |
| **Direct port forward + Caddy** | Open 443, let Caddy handle TLS | Exposes your IP, but no third party |
| **frp / rathole** | Self-hosted tunnel via a VPS | You control the relay, but need a VPS |

The honest tradeoff: **Cloudflare Tunnels are genuinely convenient, and the alternatives require more setup.** But "convenient" is exactly what the trust problem is about.

### Phase 4: Migrate Workers & Pages

This is the hard one. If your code runs on Workers or Pages, you have to actually move it:

- **Pages →** any static host (GitHub Pages, Netlify, Vercel, or your own server with Caddy)
- **Workers →** a serverless runtime you control, or just a small VPS running your functions
- **KV / D1 / R2 →** Redis, Postgres, or S3-compatible storage you control

This is a real migration, not a config change. Budget time for it.

### Phase 5: Kill the Analytics Injection

Even if you stay on Cloudflare for other reasons, **turn off the silent analytics:**

1. Cloudflare dashboard → **Analytics & Logs** → **Web Analytics**
2. Disable the site (or delete the beacon)
3. Verify the `cloudflareinsights.com` request is gone from your network tab

And if you want analytics you actually control, [self-host Umami or Plausible](/blog/2026-08-10-self-hosted-web-analytics-2026/) — which is the whole point of that post.

---

## What "Self-Hosted" Should Actually Mean

Here's the thing I keep coming back to.

We call ourselves "self-hosters," but a lot of us are running a stack where the single most important layer — the request path — is owned by a third party. We self-host the app, but we outsource the trust.

That's not self-hosting. That's **self-hosting the parts that are easy, and outsourcing the parts that matter.**

The request path is where the trust lives. It's where TLS happens, where analytics get injected, where traffic gets inspected, where "legitimate" gets decided. If you don't control that, you don't control your stack — you just control the parts Cloudflare lets you control.

Moving off Cloudflare isn't about hating Cloudflare. It's about being honest about what "self-hosted" means, and whether your stack actually lives up to the word.

---

## The Bottom Line

Cloudflare is useful. I've recommended them, and I'll probably recommend them again for specific use cases. But the silent analytics injection is a reminder of something we keep forgetting:

**Every third party you put in your request path is a third party that can see, log, and modify your traffic — and their incentives are not your incentives.**

The audit is the point. Know what you're using Cloudflare for. Know what they're doing in return. And if the answer makes you uncomfortable, you now have a playbook to move off.

Start with the DNS. End with the analytics beacon. And the next time you call yourself a self-hoster, make sure it's actually true.

---

*Last updated: August 21, 2026. The analytics-injection signal (653 points, recurring since August 18) was observed in my own traffic monitoring and is still climbing as of this writing. This post is the missing "audit + move off Cloudflare" playbook that complements our existing Tunnels, Workers, and analytics coverage.*

**Related Reading:**
- [Cloudflare Tunnels: Expose Your Homelab Without Opening a Single Port](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/)
- [Self-Hosted Web Analytics in 2026: Ditch Google Analytics for Good](/blog/2026-08-10-self-hosted-web-analytics-2026/)
- [WireGuard + Pi-hole: The Privacy Stack That Replaces Your ISP's DNS](/blog/2026-04-21-wireguard-pihole-privacy-stack/)
- [Self-Hosted Email in 2026: A Stack That Actually Delivers to Gmail](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail/)
