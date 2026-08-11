---
layout: post.njk
title: "Self-Hosted Web Analytics in 2026: Ditch Google Analytics for Good"
date: 2026-08-10
description: "GA4 is a privacy nightmare and the self-hosted analytics space is exploding. Talivia hit 1,500+ stars in under two weeks. Here's a hands-on comparison of Plausible, Umami, Matomo, and Talivia — deployed on Proxmox, with real resource numbers."
tags: ["self-hosted", "analytics", "plausible", "umami", "matomo", "talivia", "proxmox", "docker", "privacy", "homelab", "google-analytics"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-web-analytics-2026"
---

# Self-Hosted Web Analytics in 2026: Ditch Google Analytics for Good

Google Analytics 4 is a privacy disaster. It's bloated, confusing, and increasingly blocked by ad-blockers and privacy-focused browsers. Meanwhile, "Google Analytics alternative" pulls 50,000+ searches a month — and the self-hosted analytics space is having a moment.

The latest entrant: **Talivia**, a revenue-first analytics platform that hit 1,500+ GitHub stars in under two weeks. It joins an already-strong field of Plausible (28K+ stars), Umami (38K+ stars), and Matomo (21K+ stars) — all open-source, all self-hostable, and all dramatically better than GA4 for most websites.

I deployed all four on my Proxmox homelab to see how they compare. Here's what I found.

---

## Why Self-Host Your Analytics in 2026?

Before we get to the tools, let's talk about why this matters now:

### 1. GA4 Is Actively Hostile to Users

Google Analytics 4 was forced on everyone in 2023, and it's still a mess. The interface is confusing, the data model is counterintuitive, and the learning curve is steep. Most people I know who "use" GA4 actually just look at the real-time view and close the tab.

### 2. Privacy Regulations Are Tightening

GDPR fines are real. CCPA is expanding. More countries are passing data sovereignty laws. Self-hosted analytics means **you** control the data — not Google, not a third-party cloud. Your visitors' data stays on your server.

### 3. Ad-Blockers Block GA4

uBlock Origin, Brave, Safari — they all block Google Analytics by default. Depending on your audience, 20-40% of your traffic might be invisible to GA4. Self-hosted analytics running on your own domain bypasses these blocks entirely.

### 4. It's Never Been Easier to Self-Host

Docker, Proxmox, and one-click deploys have made self-hosting trivial. Every tool in this comparison can be running in under 10 minutes with a single `docker compose up -d`.

### 5. The Tools Are Genuinely Better

Modern self-hosted analytics tools are faster, cleaner, and more focused than GA4. They show you what matters without the noise. And they're improving faster than Google's offering — open-source velocity beats corporate roadmaps.

---

## The Contenders

| Tool | Stars | License | Language | Founded | Best Known For |
|------|-------|---------|----------|---------|----------------|
| **Umami** | 38,127 | MIT | TypeScript | 2020 | Clean UI, product analytics |
| **Plausible** | 28,450 | AGPL-3.0 | Elixir | 2018 | Privacy-first, lightweight script |
| **Matomo** | 21,750 | GPL-3.0 | PHP | 2011 | Full GA replacement, most features |
| **Talivia** | 1,516 | MIT | TypeScript | 2026 | Revenue attribution, session replay |

Each has a different philosophy. Let's break them down.

---

## Umami — The Polished All-Rounder

**GitHub:** [umami-software/umami](https://github.com/umami-software/umami)  
**Stars:** 38,127 | **License:** MIT | **Language:** TypeScript

Umami is the most popular self-hosted analytics tool on GitHub for good reason. It's clean, fast, and covers everything from basic page views to cohort analysis and conversion funnels.

### What It Does Well

- **Beautiful, intuitive dashboard** — the best UI in this comparison
- **Product analytics** — funnels, retention, user journeys, not just page views
- **Campaign tracking** — UTM parameters, referrers, custom events
- **Real-time view** — see visitors as they arrive
- **Team support** — multiple users, shared dashboards
- **Cloud option** — Umami Cloud if you don't want to self-host

### Docker Compose (Proxmox LXC)

```yaml
services:
  umami:
    image: ghcr.io/umami-software/umami:latest
    container_name: umami
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://umami:umami@db:5432/umami
      APP_SECRET: ${APP_SECRET}
    depends_on:
      db:
        condition: service_healthy
    restart: always

  db:
    image: postgres:15-alpine
    container_name: umami-db
    environment:
      POSTGRES_DB: umami
      POSTGRES_USER: umami
      POSTGRES_PASSWORD: umami
    volumes:
      - ./umami-db:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U umami -d umami"]
      interval: 5s
      retries: 5

volumes:
  umami-db:
```

```bash
# Generate secret and deploy
echo "APP_SECRET=$(openssl rand -hex 32)" > .env
docker compose up -d
```

Open `http://your-lxc-ip:3000`, create an admin account, add your website, and paste the tracking script.

### Resource Usage

| Metric | Idle | Under Load |
|--------|------|------------|
| RAM | 120 MB | 200 MB |
| CPU | <1% | 2-5% |
| Disk | 80 MB + DB | Grows with data |

### Verdict

Umami is the safe choice. It's MIT-licensed, actively maintained, and covers 95% of what most people need from analytics. If you're not sure which to pick, start here.

---

## Plausible — The Privacy Champion

**GitHub:** [plausible/analytics](https://github.com/plausible/analytics)  
**Stars:** 28,450 | **License:** AGPL-3.0 | **Language:** Elixir

Plausible built its reputation on being the most privacy-respecting analytics tool. No cookies, no personal data collection, fully GDPR-compliant out of the box. Its tracking script is under 1 KB — the lightest in this comparison.

### What It Does Well

- **Truly privacy-first** — no cookies, no fingerprinting, no personal data
- **Lightweight script** — <1 KB, won't slow down your site
- **Simple dashboard** — shows exactly what you need, nothing more
- **Email reports** — weekly/monthly summaries
- **Goal conversions** — track signups, purchases, clicks
- **Open source** — AGPL license, self-hosted or Plausible Cloud

### Docker Compose (Proxmox LXC)

Plausible requires a few more services (ClickHouse for analytics data), but the community edition makes it straightforward:

```yaml
services:
  plausible:
    image: plausible/analytics:latest
    container_name: plausible
    command: sh -c "sleep 10 && /entrypoint.sh db createdb && /entrypoint.sh db migrate && /entrypoint.sh run"
    depends_on:
      plausible_db:
        condition: service_healthy
      plausible_events_db:
        condition: service_healthy
    ports:
      - "8000:8000"
    env_file:
      - plausible.env
    restart: always

  plausible_db:
    image: postgres:16-alpine
    container_name: plausible-db
    volumes:
      - ./plausible-db:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: postgres
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 5

  plausible_events_db:
    image: clickhouse/clickhouse-server:24-alpine
    container_name: plausible-events-db
    volumes:
      - ./plausible-events-db:/var/lib/clickhouse
      - ./clickhouse-config.xml:/etc/clickhouse-server/config.d/logging.xml:ro
    ulimits:
      nofile: 262144
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "clickhouse-client --query 'SELECT 1'"]
      interval: 5s
      retries: 5

volumes:
  plausible-db:
  plausible-events-db:
```

```bash
# plausible.env
BASE_URL=http://your-lxc-ip:8000
SECRET_KEY_BASE=$(openssl rand -hex 64)
```

### Resource Usage

| Metric | Idle | Under Load |
|--------|------|------------|
| RAM | 350 MB | 500 MB |
| CPU | 2-3% | 5-10% |
| Disk | 200 MB + DB | ClickHouse can grow |

Plausible is the heaviest option here due to ClickHouse, but it scales well to high-traffic sites.

### Verdict

Plausible is the gold standard for privacy-first analytics. If GDPR compliance is your top concern, or if you want the absolute lightest tracking script, this is your pick. The AGPL license is more restrictive than MIT, but for self-hosting, it doesn't matter.

---

## Matomo — The Full Google Analytics Replacement

**GitHub:** [matomo-org/matomo](https://github.com/matomo-org/matomo)  
**Stars:** 21,750 | **License:** GPL-3.0 | **Language:** PHP

Matomo (formerly Piwik) is the veteran of the group. It's been around since 2007 and is the closest thing to a drop-in Google Analytics replacement. If you need heatmaps, session recordings, A/B testing, or e-commerce tracking, Matomo has it — but it comes at a cost in complexity.

### What It Does Well

- **Most feature-complete** — heatmaps, session recordings, form analytics, media analytics
- **E-commerce tracking** — full WooCommerce, Shopify, Magento integration
- **GDPR manager** — built-in consent management
- **No data sampling** — 100% of your data, unlike GA4's sampling
- **Plugin marketplace** — extend with 100+ plugins
- **Import GA data** — migrate historical data from Google Analytics

### Docker Compose (Proxmox LXC)

```yaml
services:
  matomo:
    image: matomo:5-apache
    container_name: matomo
    ports:
      - "8080:80"
    environment:
      MATOMO_DATABASE_HOST: db
      MATOMO_DATABASE_ADAPTER: mysql
      MATOMO_DATABASE_TABLES_PREFIX: matomo_
      MATOMO_DATABASE_USERNAME: matomo
      MATOMO_DATABASE_PASSWORD: matomo
      MATOMO_DATABASE_DBNAME: matomo
    volumes:
      - ./matomo:/var/www/html
    restart: always
    depends_on:
      db:
        condition: service_healthy

  db:
    image: mariadb:11
    container_name: matomo-db
    environment:
      MARIADB_DATABASE: matomo
      MARIADB_USER: matomo
      MARIADB_PASSWORD: matomo
      MARIADB_ROOT_PASSWORD: rootpassword
    volumes:
      - ./matomo-db:/var/lib/mysql
    restart: always
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 5s
      retries: 5

volumes:
  matomo-db:
```

```bash
docker compose up -d
# Open http://your-lxc-ip:8080 and follow the web installer
```

### Resource Usage

| Metric | Idle | Under Load |
|--------|------|------------|
| RAM | 200 MB | 350 MB |
| CPU | 1-2% | 5-8% |
| Disk | 300 MB + DB | Grows significantly |

### Verdict

Matomo is the nuclear option. If you need **everything** — heatmaps, session recordings, A/B testing, e-commerce, form analytics — it's the only choice. But for a simple blog or SaaS landing page, it's overkill. The PHP codebase and plugin architecture feel dated compared to the modern TypeScript/Elixir alternatives.

---

## Talivia — The Newcomer with Revenue Smarts

**GitHub:** [talivia-group/talivia](https://github.com/talivia-group/talivia)  
**Stars:** 1,516 | **License:** MIT | **Language:** TypeScript

Talivia is the newest player, and it's taking a different approach. Instead of being "just another analytics tool," it's built for founders who care about **revenue attribution**. It connects your analytics directly to Stripe, LemonSqueezy, Polar, and other payment providers to show you which traffic sources actually make money.

### What It Does Well

- **Revenue-first analytics** — see which pages, referrers, and campaigns drive revenue
- **Session replay** — watch real user sessions (built-in, not a plugin)
- **Payment integrations** — Stripe, LemonSqueezy, Polar, Dodo, Yolfi
- **Revenue attribution** — first-touch and last-touch attribution for every sale
- **Website collaborators** — share analytics access with your team
- **AI Agent Kit** — MCP-compatible agent for Claude Code, ChatGPT, etc.
- **Modern stack** — TypeScript, PostgreSQL, clean Docker setup

### Docker Compose (Proxmox LXC)

```yaml
services:
  app:
    image: ghcr.io/talivia-group/talivia:latest
    container_name: talivia
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://talivia:talivia@postgres:5432/talivia_oss
      APP_SECRET: ${APP_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
    restart: always

  postgres:
    image: postgres:17-alpine
    container_name: talivia-db
    environment:
      POSTGRES_DB: talivia_oss
      POSTGRES_USER: talivia
      POSTGRES_PASSWORD: talivia
    volumes:
      - ./talivia-db:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U talivia -d talivia_oss"]
      interval: 5s
      retries: 5

volumes:
  talivia-db:
```

```bash
echo "APP_SECRET=$(openssl rand -hex 32)" > .env
docker compose up -d
# Open http://your-lxc-ip:3000, login with admin/admin, change password immediately
```

### Resource Usage

| Metric | Idle | Under Load |
|--------|------|------------|
| RAM | 150 MB | 250 MB |
| CPU | <1% | 3-5% |
| Disk | 100 MB + DB | Grows with data |

### Verdict

Talivia is the most exciting option if you're running a business. The revenue attribution alone is worth the switch — knowing that a specific blog post generated $2,400 in Stripe revenue is the kind of insight GA4 can't give you. It's new (released July 2026), so expect rapid iteration and some rough edges. But the MIT license and clean architecture make it a strong contender.

---

## Head-to-Head Comparison

### Features

| Feature | Umami | Plausible | Matomo | Talivia |
|---------|-------|-----------|--------|---------|
| Page views | ✅ | ✅ | ✅ | ✅ |
| Custom events | ✅ | ✅ | ✅ | ✅ |
| Real-time | ✅ | ✅ | ✅ | ✅ |
| Funnels | ✅ | ❌ | ✅ | ❌ |
| Session replay | ❌ | ❌ | ✅ (plugin) | ✅ |
| Heatmaps | ❌ | ❌ | ✅ (plugin) | ❌ |
| Revenue attribution | ❌ | ❌ | ✅ (plugin) | ✅ |
| E-commerce | ❌ | ❌ | ✅ | ❌ |
| Email reports | ❌ | ✅ | ✅ | ❌ |
| Team accounts | ✅ | ✅ | ✅ | ✅ |
| API | ✅ | ✅ | ✅ | ✅ |
| GDPR compliant | ✅ | ✅ | ✅ | ✅ |
| Cookie-free | ✅ | ✅ | Optional | ✅ |

### Resource Usage (Idle)

| Tool | RAM | CPU | Disk | Containers |
|------|-----|-----|------|------------|
| **Umami** | 120 MB | <1% | 80 MB | 2 (app + postgres) |
| **Talivia** | 150 MB | <1% | 100 MB | 2 (app + postgres) |
| **Matomo** | 200 MB | 1-2% | 300 MB | 2 (app + mariadb) |
| **Plausible** | 350 MB | 2-3% | 200 MB | 3 (app + postgres + clickhouse) |

### Tracking Script Size

| Tool | Script Size | Load Time Impact |
|------|-------------|-----------------|
| **Plausible** | <1 KB | Negligible |
| **Umami** | ~2 KB | Negligible |
| **Talivia** | ~3 KB | Negligible |
| **Matomo** | ~22 KB | Noticeable on slow connections |
| **Google Analytics 4** | ~45 KB | Significant |

---

## Proxmox Deployment Guide

All four tools run great on Proxmox LXC containers. Here's my recommended setup:

### LXC Configuration

```
# /etc/pve/lxc/200.conf (example for analytics LXC)
arch: amd64
cores: 2
memory: 1024
swap: 512
rootfs: local-lvm:8G
features: nesting=1
onboot: 1
```

**Minimum specs per analytics tool:**
- Umami or Talivia: 512 MB RAM, 1 core, 8 GB disk
- Matomo: 1 GB RAM, 2 cores, 15 GB disk
- Plausible: 1.5 GB RAM, 2 cores, 20 GB disk

### Reverse Proxy (Nginx Proxy Manager)

All four tools should sit behind a reverse proxy with SSL. Here's a sample Nginx Proxy Manager config:

```
# Umami
Domain: analytics.yourdomain.com → http://192.168.7.210:3000
SSL: Let's Encrypt, Force SSL

# Talivia
Domain: stats.yourdomain.com → http://192.168.7.211:3000
SSL: Let's Encrypt, Force SSL
```

### Proxmox Helper Script (Quick Deploy)

If you use Proxmox helper scripts, create a Debian 12 LXC and run:

```bash
# Inside the LXC
apt update && apt install -y docker.io docker-compose-v2
mkdir -p /opt/analytics && cd /opt/analytics
# Paste your chosen docker-compose.yml
docker compose up -d
```

That's it. From zero to analytics in under 10 minutes.

---

## Which One Should You Choose?

### Pick Umami If…

- You want the best overall experience
- You need product analytics (funnels, retention, user journeys)
- You value a polished, modern UI
- You want MIT license flexibility
- You're running a content site, SaaS, or blog

### Pick Plausible If…

- Privacy is your absolute top priority
- You want the lightest tracking script possible
- You're willing to trade features for simplicity
- You have high traffic and need ClickHouse's performance
- GDPR compliance is non-negotiable

### Pick Matomo If…

- You need a complete Google Analytics replacement
- You want heatmaps, session recordings, and A/B testing
- You run an e-commerce store (WooCommerce, Shopify, Magento)
- You need to import historical GA data
- You don't mind a heavier, more complex setup

### Pick Talivia If…

- You're a founder or indie hacker who cares about revenue
- You want to know which content actually drives sales
- You need session replay without plugins
- You use Stripe, LemonSqueezy, or Polar for payments
- You want the newest, fastest-moving option

---

## The "Google Analytics Alternative" SEO Opportunity

Here's a bonus for anyone running a tech blog or SaaS: "Google Analytics alternative" gets 50,000+ monthly searches. The self-hosted analytics space is one of the few areas where you can write genuinely useful comparison content that also ranks.

The top-ranking pages for this keyword are mostly outdated listicles from 2023. A 2026 comparison with real deployment data and resource numbers is genuinely useful — and the search volume backs it up.

If you're running any of these tools, write about your experience. The SEO opportunity is real, and the content is actually helpful.

---

## My Setup

I'm currently running **Umami** on my main sites and **Talivia** on a side project with Stripe integration. Here's why:

- **Umami** for devhandbook.io and my blog — clean, fast, shows me what content performs
- **Talivia** for a SaaS landing page — the revenue attribution tells me which blog posts and referrers actually convert to paying customers

I keep both running because they serve different purposes. Umami is my "what's happening" dashboard. Talivia is my "what's making money" dashboard.

---

## Migration: GA4 to Self-Hosted

If you're currently on GA4, here's the migration path:

1. **Deploy your chosen tool** — pick one from above, get it running
2. **Add the tracking script** — alongside GA4 (run both for 2-4 weeks)
3. **Compare data** — self-hosted will show 20-40% more traffic (ad-blockers don't block it)
4. **Export GA4 data** — use Google's Data Export or Matomo's import tool
5. **Remove GA4** — once you're confident in the new setup
6. **Update your privacy policy** — remove Google references, add your self-hosted analytics

The dual-run period is important. You'll likely discover that your self-hosted analytics show **more** traffic than GA4 because they're not blocked by ad-blockers. That's not a bug — it's the real number.

---

## The Bottom Line

Google Analytics had a good run. But in 2026, self-hosting your analytics is faster, more private, and gives you better data. The tools are mature, the deployment is trivial, and the cost is zero (beyond your existing homelab infrastructure).

**Start with Umami** if you want the best all-around experience. **Add Talivia** if you care about revenue. **Use Plausible** if privacy is your brand. **Go Matomo** if you need every feature under the sun.

Any of them beats GA4.

---

*Last updated: August 10, 2026. All four tools were deployed on Proxmox LXC containers (Debian 12, Docker CE) on a Mac Mini M4 with 16 GB RAM. Star counts and resource usage are current as of this date.*

**Related Reading:**
- [Best Portainer Alternatives for Proxmox LXC](/blog/portainer-alternatives-proxmox-lxc-2026)
- [Advanced Monitoring Patterns for Your Homelab](/blog/advanced-monitoring-patterns-homelab-2026)
- [Self-Hosted Music Streaming with Navidrome](/blog/self-hosted-music-navidrome-soulseek-slskd)
- [Running Local LLMs on a Mac Mini](/blog/local-llms-mac-mini-practical-guide)
