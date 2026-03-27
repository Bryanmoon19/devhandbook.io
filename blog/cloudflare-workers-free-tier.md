---
layout: post.njk
title: "What You Can Build for Free with Cloudflare Workers"
date: 2026-03-26
description: "Cloudflare Workers' free tier is surprisingly powerful. Here's what you can actually ship without spending a dollar."
tags: ["cloudflare", "serverless", "devtools", "free-tier"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/cloudflare-workers-free-tier"
---

Most developers hear "free tier" and immediately start looking for the catch. With Cloudflare Workers, the catch is almost embarrassingly small. The free plan gives you 100,000 requests per day, global edge deployment across 300+ cities, zero cold starts, and access to KV storage — and it costs exactly nothing. Here's what you can realistically build and ship on that budget.

## What the Free Tier Actually Includes

Let's be specific, because the marketing page buries the good stuff:

- **100,000 requests/day** — resets daily, more than enough for most personal projects and small tools
- **10ms CPU time per request** — wall clock is much longer, 10ms is just compute
- **Workers KV** — 100,000 reads/day, 1,000 writes/day, 1,000 deletes/day, 1 GB storage
- **No cold starts** — Workers use V8 isolates, not containers. Your function is warm instantly, every time, everywhere
- **Global by default** — your Worker runs at the edge closest to the user automatically, no configuration needed
- **Custom domains** — point your own domain to a Worker on the free plan

What you don't get on free: Durable Objects, R2 storage, D1 (SQLite), Workers AI, or Cron Triggers (that last one is notable — you'll need a workaround for scheduled tasks).

## 1. A Plex Invite System

If you run a Plex server for friends and family, you know the invite process is clunky — you either hand out your email, use the web UI one at a time, or use third-party tools that require self-hosting. A Cloudflare Worker solves this cleanly.

Build a simple Worker that:
- Serves a small HTML form asking for the requester's email and a passphrase
- Validates the passphrase against a KV-stored secret
- Calls the Plex API to send a library share invite to the submitted email
- Logs the invite to KV so you have a record

The whole thing is under 80 lines of JavaScript. You get a clean URL like `invite.yourdomain.com` that you can share, and friends self-service their own Plex access without you doing anything manually. Rate limit by IP using the `CF-Connecting-IP` header to prevent abuse.

## 2. A Link Shortener

This is the classic Workers demo for good reason — it's genuinely useful and demonstrates KV perfectly. The pattern:

```js
export default {
  async fetch(request, env) {
    const slug = new URL(request.url).pathname.slice(1);
    const target = await env.LINKS.get(slug);
    if (target) return Response.redirect(target, 302);
    return new Response('Not found', { status: 404 });
  }
};
```

Add slugs to KV via the Cloudflare dashboard or the Wrangler CLI (`wrangler kv:key put --binding LINKS slug https://destination.com`). You get a permanent short URL that redirects instantly from the global edge. No database, no server, no maintenance.

Want a dashboard to manage links? Build a second Worker that serves an HTML admin panel, protected by a secret token in a header. Keep it simple — a form that writes to KV is all you need.

## 3. An API Proxy with Rate Limiting

Some third-party APIs don't support CORS, or you want to add auth, logging, or transformation before data hits your frontend. A Worker is perfect for this.

More interesting: add rate limiting per user using KV. Store a counter with a TTL:

```js
const key = `ratelimit:${clientIp}`;
const current = parseInt(await env.CACHE.get(key) || '0');
if (current >= 50) return new Response('Rate limited', { status: 429 });
await env.CACHE.put(key, String(current + 1), { expirationTtl: 3600 });
```

This gives you 50 requests per hour per IP. Adjust as needed. No Redis, no infrastructure — just KV and a few lines of code. You can add API key validation the same way, checking a submitted key against a KV lookup table.

This pattern is especially useful for protecting expensive AI API calls — add a Worker in front of OpenAI, Anthropic, or any LLM provider, and you get auth + rate limiting + logging for free.

## 4. Static Sites with Edge Logic

Cloudflare Pages (also free, also excellent) handles static site hosting. But sometimes you need a Worker alongside a static site to add dynamic behavior — A/B testing, geolocation-based redirects, authentication walls, or personalized content.

A Worker can intercept requests to your Pages site and modify the response before it reaches the user. Want to show a different hero image to visitors from Europe? Read `request.cf.country`. Want to A/B test a landing page? Read a cookie, set one if it doesn't exist, and route accordingly. Want to password-protect a staging site without setting up auth infrastructure? A Worker with Basic Auth takes about 20 lines.

The combination of Pages + Workers gives you a static site with programmable edge logic, globally distributed, entirely free up to reasonable traffic volumes.

## When to Upgrade to Paid

The Workers paid plan ($5/month) makes sense when:

- You exceed 100k requests/day consistently (the paid plan is 10M requests/month, then $0.30/million)
- You need Cron Triggers for scheduled jobs
- You need Durable Objects for stateful coordination or WebSocket handling
- You need R2 for object storage (S3-compatible, egress is free)
- You need D1 for a real SQL database at the edge

At $5/month, the paid plan is one of the better deals in infrastructure. But the free tier genuinely covers a lot of ground — if you're building personal tools, small SaaS MVPs, or internal utilities, you can ship real things without touching your credit card.

## The Global Edge Advantage

What doesn't show up in the free tier feature list but matters enormously: Workers runs in 300+ cities. When a user in Tokyo hits your Worker, it runs in Tokyo. When someone in São Paulo makes a request, it runs in São Paulo. You don't configure this. You don't pay extra for it. It just happens.

For a traditional server or even a typical serverless function, you pick a region and users far from that region get slower responses. With Workers, latency is consistently low everywhere on Earth. That's not a minor detail — it's a fundamental architectural advantage that normally costs significant money to replicate.

## Getting Started

Install Wrangler, Cloudflare's CLI:

```bash
npm install -g wrangler
wrangler login
wrangler init my-worker
cd my-worker
wrangler dev  # local development with live reload
wrangler deploy  # ship it
```

The local dev experience with `wrangler dev` is solid — it emulates the Workers runtime locally, including KV bindings, so you can build and test without deploying on every change.

The free tier isn't a teaser. It's a serious platform for real projects. Start building.
