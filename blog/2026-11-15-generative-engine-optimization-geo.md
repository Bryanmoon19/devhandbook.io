---
layout: post.njk
title: "Generative Engine Optimization (GEO): How to Get Your Site Cited by ChatGPT, Perplexity, and Gemini"
date: 2026-11-15
description: "AI search is eating classic search, and 'Generative Engine Optimization' (GEO) is the new skill nobody's written a good dev guide for yet. Here's what GEO actually is, how it differs from SEO, the metrics that matter, and a self-hosted stack (GEOInflow + log analysis) to track which LLMs cite your site."
tags: ["geo", "generative-engine-optimization", "seo", "ai-search", "chatgpt", "perplexity", "gemini", "self-hosted", "analytics", "ai-crawlers", "content-marketing", "developer-tools", "marketing"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-15-generative-engine-optimization-geo/"
affiliate: false
cta: true
---

# Generative Engine Optimization (GEO): How to Get Your Site Cited by ChatGPT, Perplexity, and Gemini

For twenty years, the playbook was the same: write for Google, get crawled, rank, get clicks. Then, quietly and quickly, the destination changed. People stopped typing queries into a search box and started asking an AI assistant. And when ChatGPT or Perplexity answers, it doesn't send ten blue links — it *cites sources*. That citation is the new click. The discipline of getting those citations is called **Generative Engine Optimization**, or **GEO**.

Here's the thing that makes this worth writing about *today*: the term is almost unclaimed. There are a handful of research papers, a few marketing-newsletter hot takes, and a couple of brand-new open-source tools — but no authoritative, dev-facing explainer aimed at the self-hoster and indie-builder crowd. This post is that, written from the awkward-but-useful position of being a content site that is *itself* trying to figure out how to get cited.

I'm not going to pretend I've solved it. What I'll give you is a clear mental model, the metrics that actually matter, and a working self-hosted stack for tracking it — because "am I getting cited?" is a question you should be able to answer with your own logs, not a marketer's dashboard.

---

## What GEO Actually Is (and Why It's Not SEO)

The shortest definition: **GEO is the practice of making your content more likely to be selected, cited, and surfaced by AI-powered answer engines** — ChatGPT, Perplexity, Google's AI Overviews, Gemini, Claude, and the growing crop of AI search products.

It sounds like SEO rebranded, and there's overlap, but the mechanics are fundamentally different:

| | Classic SEO | GEO |
|---|---|---|
| **Output** | A ranked link you click | A cited source inside an answer |
| **Signal** | Backlinks, keywords, crawlability | Citation-worthiness, extractability, authority signals |
| **Win** | Click-through to your page | Being *named* and *quoted* as the answer |
| **Measured by** | Rankings, organic traffic | AI referrals, citation presence, snippet extraction |
| **Gatekeeper** | Crawl → index → rank | Crawl → train/fetch → *choose to cite* |

The key difference is the last row. Google's job is to rank a list and let *you* choose. An answer engine's job is to *commit* — to synthesize and pick one (or a few) sources to stand behind. That means:

1. **Being crawled is no longer enough.** The AI has to find your page, then *decide* your content is the best extractable answer.
2. **Citations are binary-ish and winner-take-most.** Ten sites can rank for a query; one site gets quoted for it.
3. **Your content has to be quotable, not just keyword-dense.** The model pulls *claims* it can cite, so clean, factual, well-structured sentences beat keyword soup every time.

None of this is settled science — the field is maybe two years old, and "GEO" as a discipline is being defined in real time. That's exactly why owning the definitional content now has compounding value.

---

## The Metric That Matters: AI Referrals (and How They Show Up)

Before you can optimize, you need to know what success looks like. It's not "rank #1." It's a handful of new signals, most of which your existing analytics *can't see*:

**1. AI search referrals.** When a user clicks from a Perplexity or ChatGPT answer through to your site, the referrer isn't a search engine — it's an AI product (often masked, proxied, or in-app). Google Analytics lumps these into "Direct" or "Other" unless you specifically instrument for them. This is the single most important number for GEO, and it's the one most people are silently missing.

**2. Crawler activity.** The big AI labs run their own crawlers — OpenAI's `GPTBot`, Anthropic's `ClaudeBot`, Google's `Google-Extended`, Perplexity's crawler, and more. If those bots are hitting your pages, you're *in the candidate pool*. If they're not, you're invisible to the answer engine no matter how good the content is. Your raw server logs (or Cloudflare's log stream) tell you exactly who's visiting.

**3. Citation presence.** Is your domain actually being cited in answers for your target queries? This is the hardest to measure (the answer engines don't expose a clean API for it), but you can sample it manually and, increasingly, with tools.

**4. Coverage gaps.** Which of your important pages have *never* been crawled by an AI bot? A sitemap that Google indexes but GPTBot has never touched is a page that can't possibly be cited.

The uncomfortable truth most "GEO tools" gloss over: **crawl logs establish that a bot *visited*. They don't prove you got cited.** Indexing, training, citation, and ranking are four separate events, and each needs its own evidence. Anyone who tells you their tool "guarantees AI visibility" is selling you a map and calling it the territory.

---

## The Self-Hosted GEO Stack

Here's the stack I'm actually running (or standing up) on this site, because — full honesty — this is the meta part: devhandbook.io is a content site, and I want to see which LLMs cite it. So the "how to instrument your own site" advice below is not theoretical. It's the same thing I'm doing.

### 1. GEOInflow — the anchor tool

**[GEOInflow](https://github.com/yaojingang/GEOInflow)** (847★, TypeScript, MIT) is a self-hosted web + AI-crawler analytics platform built *specifically* for GEO. It landed in October 2026 and is the most complete open-source option I've found. It does four things that map directly to the metrics above:

- **AI crawler analytics** — a built-in catalog of crawler identities (OpenAI, Anthropic, Perplexity, Google, Microsoft, ByteDance, Baidu, Kimi, Tencent Hunyuan, and more), each tracked with its purpose (training vs. AI search vs. user-triggered) and its verification status. It distinguishes a `User-Agent` claim from an official-IP match, which matters because lying about your crawler's identity is trivial.
- **Content coverage** — import your sitemap/CSV/JSON inventory and see which pages have been crawled, which have *never* been crawled, and where requests are failing (HTTP status, caching, latency).
- **AI referral tracking** — browser tracking that recognizes AI-search referrers and ties them to landing pages, goals, and conversions — so you can see not just "did they cite us" but "did that citation actually convert."
- **Crawler evidence** — request volume, trends, and risk signals, kept separate from the "did it lead to a citation" question so you don't over-claim.

It runs as a normal self-hosted app (the quick-start and deployment docs are in English; the deeper reference guides are currently Simplified Chinese — worth knowing before you dive in). For most of you, the docker-compose route is the on-ramp. The project ships a `docker-compose.liekan.yml` that defines five services — the Next.js app, a log worker, an analytics worker, Redis (as the analytics cache), and PostgreSQL. I've condensed it to the essentials so you can see the shape of it:

```yaml
services:
  app:
    image: liekan:1.2.0
    build:
      context: .
      dockerfile: Dockerfile.liekan
    ports:
      - '127.0.0.1:3002:3000'
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      APP_SECRET: ${APP_SECRET:?APP_SECRET required}
      TWO_FACTOR_ENCRYPTION_KEY: ${TWO_FACTOR_ENCRYPTION_KEY:?TWO_FACTOR_ENCRYPTION_KEY required}
      DISABLE_TELEMETRY: '1'
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  log-worker:
    image: liekan:1.2.0
    command: ['node', 'dist/liekan-worker.mjs']
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      APP_SECRET: ${APP_SECRET:?APP_SECRET required}
      DISABLE_TELEMETRY: '1'
    depends_on:
      app:
        condition: service_healthy
    restart: unless-stopped

  analytics-cache:
    image: redis:7.4-alpine
    command: ['redis-server', '--maxmemory', '256mb', '--maxmemory-policy', 'allkeys-lru', '--appendonly', 'no']
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    shm_size: '256mb'
    ports:
      - '127.0.0.1:15435:5432'
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-liekan}
      POSTGRES_USER: ${POSTGRES_USER:-liekan}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD required}
    volumes:
      - liekan-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  liekan-data:
  liekan-geography:
```

In practice you don't hand-wire this — the repo's `sh scripts/liekan-deploy.sh` generates a private `.env` with random secrets, builds the image, runs migrations, imports a sanitized example site so you can explore before wiring in your own, and starts everything (the first-login credentials are `admin` / `liekan`, which you change immediately). The deploy script wants at least **6 GiB of Docker memory** (8 GiB + 2 CPUs recommended) because the image is built from source. Once it's up, you create a website, drop the tracking script on your pages, and optionally wire Cloudflare log ingestion (OAuth-scoped `zone.read logs.read`) so crawl logs flow in automatically.

### 2. Your own server logs — the zero-dependency baseline

You don't strictly need a new tool to start. If you're on Cloudflare (as this site is), the log stream already records every AI crawler that hits you. A simple grep over your access logs for the known bot User-Agents gives you a free, honest baseline:

```bash
# Which AI crawlers visited in the last N days?
grep -Ei 'GPTBot|ClaudeBot|Google-Extended|PerplexityBot|Bytespider|Amazonbot|cohere|anthropic-ai|OAI-SearchBot|ChatGPT-User' access.log | \
  awk '{print $NF}' | sort | uniq -c | sort -rn
```

That one-liner will tell you more about your GEO reality in five minutes than most marketing dashboards will in a month. It's also the "trust but verify" layer: whatever a tool reports, your raw logs are the ground truth.

### 3. GEORank and the companion tools

The space is young, so the tooling is proliferating fast. Alongside GEOInflow:

- **[GEORank](https://github.com/yaojingang/GEORank)** (539★) — from the same author, an open-source "GEO ranking" platform that tries to score your visibility across generative engines.
- **[AutoGEO](https://github.com/cxcscmu/AutoGEO)** (238★, ICLR'26) — a research framework for *automatically learning* what generative engines prefer. More of a "read the paper" artifact than a run-in-production tool, but it's where the academic frontier is.
- **Curated lists** — [awesome-generative-engine-optimization](https://github.com/amplifying-ai/awesome-generative-engine-optimization) (542★), [Awesome-GEO](https://github.com/DavidHuji/Awesome-GEO), and [awesome-geo](https://github.com/luka2chat/awesome-geo) are good starting points for the fast-moving resource landscape.

The pattern to notice: the whole tooling ecosystem is weeks-to-months old. That's both the opportunity (early ranking) and the warning (don't over-invest in any one tool's assumptions — the ground keeps moving).

---

## What Actually Moves the Needle (the honest part)

I've spent the last stretch reading the emerging GEO literature and the field notes of people who do this for a living, and here's the synthesis that survives contact with reality:

**1. Write for extractability, not density.** Answer engines pull *claims* they can cite. A single, clear, well-attributed sentence ("Brave Search now accepts agentic payments via x402") is worth more than ten paragraphs of keyword stuffing. Put the answer up front, then elaborate. This is the single biggest shift from classic SEO, where you often bury the lede to keep people scrolling.

**2. Structure is a citation signal.** Headings, short paragraphs, tables, numbered lists, and explicit definitions make your content trivially easy for a model to segment and quote. The table above comparing SEO vs. GEO is *exactly* the kind of thing an answer engine loves to lift into a response — and cite back to you.

**3. Earn genuine authority.** The answer engines are trying to avoid citing garbage. Real first-hand experience ("I ran this in my homelab"), verifiable claims, linked sources, and a consistent domain of expertise all read as trust signals. A site that publishes "we tested this" beats a site that publishes "10 best X (2026)" every time — and that gap is widening.

**4. Make sure the crawlers can even reach you.** Check your `robots.txt` isn't blocking the AI bots you *want* (Google-Extended and GPTBot are commonly blocked by sites that then wonder why they're invisible to AI). Check your key pages aren't paywalled or JS-only. An answer engine can't cite what it can't read.

**5. Track referrals before you trust any dashboard.** Until you've verified AI referrals in your own logs or a tool you control, you're optimizing blind. This loops back to the stack above.

---

## Should You Care Right Now?

My honest read, separated by who you are:

- **If you run a content site or blog** — yes, and soon. AI search is eating organic traffic, and the sites that understand "citations are the new clicks" will be the ones that survive the transition. The term "GEO" being nearly unclaimed today is a window that closes fast.
- **If you're a self-hoster or indie builder** — this is a genuinely useful new category to know, and it's *also* a great excuse to stand up a self-hosted analytics tool you control instead of handing more data to Google. The stack above is free and yours.
- **If you sell SEO services** — learn this now or be the person explaining rotary phones in 2027. The market is already shifting under you.

I'll keep this updated as the tooling and the answer-engine behavior evolve — both are moving fast enough that "current as of writing" is a real caveat, not a hedge. For now, the most useful next step is to pull your own access logs, see which AI crawlers are visiting (and which pages they've never touched), and get a baseline *before* you change anything.

---

*Sources: [GEOInflow](https://github.com/yaojingang/GEOInflow) and [GEORank](https://github.com/yaojingang/GEORank) repos and docs (star counts and descriptions checked live at the time of writing), [AutoGEO](https://github.com/cxcscmu/AutoGEO), the [awesome-generative-engine-optimization](https://github.com/amplifying-ai/awesome-generative-engine-optimization), [Awesome-GEO](https://github.com/DavidHuji/Awesome-GEO), and [awesome-geo](https://github.com/luka2chat/awesome-geo) curated lists. The distinction between crawl logs, indexing, citation, and ranking as separate evidence events is stated explicitly in GEOInflow's own documentation and is the honest framing this post relies on.*
