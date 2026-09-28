---
layout: post.njk
title: "Self-Hosted Social Media Scheduler: Keep Your OAuth Tokens on Your Own Box"
date: 2026-09-28
description: "Every SaaS social scheduler holds long-lived OAuth tokens to your X, LinkedIn, and Instagram accounts. That's a single breach away from someone posting as you. Self-hosted alternatives like Postiz, cogsend, and Mixpost let you schedule and publish without handing those keys to a third party. Here's the privacy argument, the comparison, and the setup."
tags: ["self-hosted", "social-media", "scheduler", "postiz", "cogsend", "mixpost", "privacy", "oauth", "buffer", "hootsuite", "homelab", "docker"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-09-28-self-hosted-social-media-scheduler-postiz-cogsend"
affiliate: true
cta: true
---

Here's a question nobody asks when they sign up for Buffer or Hootsuite: **what exactly are you handing over?**

The answer is a lot more than a username and password. When you connect a social account to any SaaS scheduler, you're authorizing it with OAuth — and the token you grant is *long-lived*. It doesn't expire after a session, or a day, or even a month. In most cases, it's valid until you explicitly revoke it. It lives in *their* database, on *their* servers, protected by *their* security — and it has permission to post, edit, and delete content on your behalf.

That token is the skeleton key to your online identity. And you just handed a copy to a third party you've never audited.

This is a genuine gap I've never covered. I've written about [self-hosted email](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail/), [self-hosted analytics](/blog/self-hosted-web-analytics-2026/), and [self-hosted auth](/blog/2026-08-08-self-hosted-auth-sso-showdown/) — but never about *outbound publishing*. The tool that posts your words to the world. That's strange, because outbound is arguably where the privacy stakes are highest: a breach in your analytics stack leaks page-view counts; a breach in your social scheduler lets someone *impersonate you publicly*.

The space is having a moment, too. **cogsend** hit 153 GitHub stars in under a week, and "buffer alternative" / "self-hosted social scheduler" are steady, evergreen search queries. The demand is real, and the tools are finally good enough. Here's the full picture.

## The Privacy Problem With SaaS Schedulers

Let me make the threat concrete, because "they hold your tokens" sounds abstract until you think through what it means.

**First, the token is the account.** OAuth scopes for social APIs are coarse. To let a scheduler post to your X account, you grant it `tweet.read` and `tweet.write` — and `tweet.write` doesn't just mean "post on schedule." It means create, reply, retweet, and in some configurations, delete. The scheduler *needs* broad write access to do its job. So the token you hand over is powerful by necessity.

**Second, the token is long-lived.** Unlike a login session, which expires, these tokens persist. Buffer, Hootsuite, and similar services store them so they can keep posting for you while you're asleep, on vacation, or haven't logged in for six months. That's the *point* of a scheduler. It's also the vulnerability: the token sits in a database 24/7, for years, waiting to be used.

**Third, you can't see the blast radius.** If a SaaS scheduler is breached, the attacker doesn't get your password — they get *worse*. They get a valid token that bypasses login entirely. No 2FA prompt, no "new device" email, no suspicious-login alert. The token *is* the login. And because you granted it months ago and forgot, you won't even remember it's out there until someone posts something you didn't write.

**Fourth, this isn't hypothetical.** Social media accounts are a prime target precisely because they're valuable and hard to recover. A hijacked X or LinkedIn account with an established audience is worth real money to spammers, crypto scammers, and impersonators. Every third party you grant a long-lived token to is one more door that has to stay locked perfectly, forever.

The fix isn't to stop using social media. It's to stop *centralizing* the keys. When you self-host your scheduler, the OAuth token lives in *your* database, on *your* server, behind *your* firewall. The only party who can post as you is you.

## What You Actually Need From a Scheduler

Before I compare the tools, let's be clear about the job. A social media scheduler is not complicated software. It does four things:

1. **Store accounts** — securely hold the OAuth tokens for your connected platforms.
2. **Compose** — a decent editor with media support and platform-specific previews.
3. **Schedule** — queue posts for a specific time, or a recurring cadence.
4. **Publish** — fire the API call at the right moment, and report back success/failure.

That's it. There's no reason this needs to be a $20/month SaaS with your data in a multi-tenant cloud. A single Docker container on a homelab box can do all four, privately.

The platforms that matter in 2026: **X (Twitter), LinkedIn, Facebook, Instagram, TikTok, YouTube, Pinterest, Bluesky, Mastodon, Threads, and Reddit.** Not every tool supports all of them, and support is the single biggest differentiator between the options below. Instagram and TikTok are the usual pain points because their APIs are restricted and often require a business account or a manual approval step.

## The Contenders

Three open-source, self-hosted schedulers actually matter right now.

| Tool | Stars (approx.) | License | Stack | Founded | Standout |
|------|-----------------|---------|-------|---------|----------|
| **Postiz** | 20K+ | AGPL-3.0 | TypeScript / Next.js | 2024 | Most platforms, most features |
| **cogsend** | 153 (and climbing) | AGPL-3.0 | TypeScript / Next.js | 2026 | New, clean, fast-moving |
| **Mixpost** | 6K+ | AGPL-3.0 / paid tiers | PHP / Laravel | 2022 | Mature, self-hosted-first |

All three are genuinely usable. They differ in maturity, platform coverage, and where they're heading.

### Postiz — the de facto standard

**GitHub:** [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app)
**Stars:** 20K+ | **License:** AGPL-3.0 | **Stack:** Next.js / TypeScript

Postiz is the one you've probably already heard of, and for good reason. It's the most feature-complete open-source scheduler, with the widest platform coverage in the category. If you need to post to a dozen platforms from one dashboard — including the annoying ones like Instagram and TikTok — Postiz is the safest bet.

It supports X, LinkedIn, Facebook, Instagram, TikTok, YouTube, Pinterest, Reddit, Bluesky, Mastodon, Threads, and more. It has an AI assistant for drafting, a media library, team support, and an analytics view. It's actively developed and backed by a company (Gitroom), so the open-source version is healthy but there's a commercial cloud tier you'll be gently steered toward.

**The tradeoff:** it's heavier than the alternatives. Next.js + PostgreSQL + Redis + S3-compatible storage is a real stack to run. If you want "set it and forget it," Postiz is the most capable but also the most to maintain.

### cogsend — the fast-moving newcomer

**GitHub:** [cogsend/cogsend](https://github.com/cogsend/cogsend)
**Stars:** 153 in under a week | **License:** AGPL-3.0 | **Stack:** Next.js / TypeScript

cogsend is the reason I'm writing this post. It went from zero to 153 stars in under a week, which in the self-hosted world is a signal worth paying attention to — the same trajectory [Talivia had in analytics](/blog/self-hosted-web-analytics-2026/).

It's a modern, clean scheduler built on the same Next.js stack as Postiz, but younger and lighter. The pitch is the same core promise — self-hosted scheduling without the SaaS lock-in — with a fresher UI and a faster-moving roadmap. Early adopters are drawn to it for exactly the reason the SEO data suggests: people searching "buffer alternative" and "self-hosted social scheduler" want *this* category, and cogsend is the newest, most eager entrant.

**The tradeoff:** it's brand new. Platform coverage is still growing, docs are thin, and you're signing up for a fast-moving target. That's not a reason to avoid it — early users get to shape the roadmap — but it *is* a reason to pin your version and back up your database.

### Mixpost — the mature, self-hosted-first veteran

**GitHub:** [inovector/mixpost](https://github.com/inovector/mixpost)
**Stars:** 6K+ | **License:** AGPL-3.0 (Lite) / commercial Pro | **Stack:** PHP / Laravel

Mixpost has been around since 2022 and is unapologetically self-hosted-first. It's built on Laravel, so if you already run PHP in your homelab, it fits your existing stack better than the two TypeScript options. It has a clean UI, supports the major platforms (X, LinkedIn, Facebook, Instagram, TikTok, YouTube, Pinterest, Mastodon), and has been battle-tested in production for years.

**The tradeoff:** the "Lite" open-source version is AGPL and intentionally feature-limited — team features, analytics, and some platform integrations are gated behind the commercial Pro tier. It's a sustainable-business model, but it means the free version is a bit more "teaser" than the other two. Still, for a single-user self-hoster, Lite covers the core schedule-and-publish loop well.

## Setup: Postiz on Proxmox (Docker Compose)

Since Postiz is the default recommendation, here's the full compose file I use on a Proxmox LXC (Debian 12, Docker CE). It's the heaviest setup of the three, but it's the one that'll still be standing in two years.

```yaml
services:
  postiz:
    image: ghcr.io/gitroomhq/postiz-app:latest
    container_name: postiz
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      MAIN_URL: "https://postiz.example.com"
      NEXT_PUBLIC_BACKEND_URL: "https://postiz.example.com/api"
      JWT_SECRET: ${JWT_SECRET}
      DATABASE_URL: "postgresql://postiz:${POSTGRES_PASSWORD}@db:5432/postiz"
      REDIS_URL: "redis://redis:6379"
      BACKEND_STORAGE_PROVIDER: "local"
      BACKEND_INTERNAL_URL: "http://localhost:5000"
      BACKEND_UPLOAD_DIRECTORY: "/uploads"
    volumes:
      - ./uploads:/uploads
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    container_name: postiz-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: postiz
      POSTGRES_USER: postiz
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postiz"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: postiz-redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
```

Create a `.env` alongside it:

```bash
JWT_SECRET=$(openssl rand -base64 48)
POSTGRES_PASSWORD=$(openssl rand -base64 24)
```

Then bring it up:

```bash
docker compose up -d
```

Point your reverse proxy (I use [Caddy](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/) or a [Cloudflare Tunnel](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/)) at `localhost:5000`, and you're done. The first time you open the dashboard you'll create an admin account, then connect your social accounts via OAuth.

## Setup: cogsend (the lighter option)

If Postiz's four-container stack feels like overkill, cogsend is the lighter lift. It still needs a database, but the footprint is smaller and the setup is faster.

```yaml
services:
  cogsend:
    image: ghcr.io/cogsend/cogsend:latest
    container_name: cogsend
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      NEXTAUTH_URL: "https://cogsend.example.com"
      DATABASE_URL: "postgresql://cogsend:${POSTGRES_PASSWORD}@db:5432/cogsend"
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    container_name: cogsend-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: cogsend
      POSTGRES_USER: cogsend
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cogsend"]
      interval: 5s
      timeout: 5s
      retries: 5
```

> **Note:** cogsend is moving fast, so the exact image name and env vars may shift between releases. Check the current `README` on the repo before you deploy — that's the one place where a brand-new project can bite you.

## The Security Angle Worth Taking Seriously

Self-hosting shifts *where* the token lives, but it doesn't remove your responsibility for protecting it. A self-hosted scheduler with a weak password and no TLS is *worse* than a SaaS one, because now the breach is your fault and it's public. Here's the minimum bar:

- **TLS everywhere.** Your scheduler's admin panel and API must be behind HTTPS. No exceptions — you're typing OAuth tokens into this thing.
- **Strong, unique admin credentials.** This isn't a throwaway dashboard. Use a password manager, and ideally put it behind an [SSO layer](/blog/2026-08-08-self-hosted-auth-sso-showdown/) so a single compromised password doesn't equal a compromised account.
- **Restrict exposure.** If you don't need to schedule from your phone while traveling, don't expose the dashboard to the public internet at all — keep it on your LAN or behind a VPN like [WireGuard + Pi-hole](/blog/2026-04-21-wireguard-pihole-privacy-stack/).
- **Back up the database.** Your OAuth tokens live in there. If you lose the DB, you have to re-authenticate every platform. [Restic + DockStash](/blog/2026-08-14-docker-backup-playbook-restic-dockstash/) is my go-to.
- **Rotate tokens occasionally.** Revoke and re-authorize your accounts every few months. It's a cheap way to invalidate any token you've forgotten about.

The point isn't paranoia. It's that self-hosting moves you from "trust a third party blindly" to "trust yourself, and do the basics." The basics are easy. Blind trust is the expensive part.

## Which One Should You Pick?

The honest answer, as usual, is "it depends on how much you want to babysit."

**Pick Postiz** if you want the most platforms, the most features, and the most likely-to-still-exist-in-two-years option. It's the safe default, and the four-container stack is worth it if you're serious about outbound publishing. This is what I'd recommend to most people reading this post.

**Pick cogsend** if you want to be early. Its 153-stars-in-a-week trajectory means an engaged community is forming right now, and early users genuinely shape a young project. If your needs are simple — X, LinkedIn, a couple of accounts, scheduled posts — cogsend is lighter and fresher. Just pin your version and expect some churn.

**Pick Mixpost** if you already run PHP/Laravel in your homelab and want the most mature self-hosted-first option, with the understanding that some features live behind the Pro tier.

For what it's worth, my own plan is Postiz on the main box for serious scheduling, and cogsend on a side LXC to watch it grow — the same "Umami for work + Talivia to watch" pattern I described for [analytics](/blog/self-hosted-web-analytics-2026/).

## The Bottom Line

Your social media accounts are your public identity, and you've been handing long-lived keys to them over to SaaS companies without thinking about it. That's the one category of self-hosting I'd argue you should care about *most*, not least — because the failure mode isn't a lost page view, it's someone else speaking as you.

The tools are ready. Postiz is mature, cogsend is the exciting newcomer, and Mixpost covers the PHP crowd. All three let you keep your OAuth tokens on your own box, behind your own firewall, under your own control.

Stop renting the keys to your own voice.

---

*Last updated: September 28, 2026. Star counts and platform coverage are current as of this date. cogsend's star count moves fast — expect it to be higher by the time you read this.*

**Related Reading:**
- [Self-Hosted Web Analytics in 2026](/blog/self-hosted-web-analytics-2026/)
- [Self-Hosted Auth & SSO Showdown](/blog/2026-08-08-self-hosted-auth-sso-showdown/)
- [Cloudflare Tunnels Homelab Guide](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/)
- [Self-Hosted Email in 2026](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail/)
- [Docker Backup Playbook with Restic & DockStash](/blog/2026-08-14-docker-backup-playbook-restic-dockstash/)
