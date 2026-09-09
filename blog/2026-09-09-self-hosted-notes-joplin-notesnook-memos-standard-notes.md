---
layout: post.njk
title: "Self-Hosted Notes in 2026: Joplin vs Notesnook vs Memos vs Standard Notes"
date: 2026-09-09
description: "Four open-source note apps, one question: which one actually syncs reliably to your phone without a cloud account? A scored head-to-head for the homelabber — sync reliability, mobile app quality, self-host difficulty, and E2E encryption — plus a working Docker Compose stack for the winner."
tags: ["joplin", "notesnook", "memos", "standard-notes", "self-hosted", "notes", "homelab", "docker", "e2e-encryption", "comparison", "markdown", "knowledge-base"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-09-09-self-hosted-notes-joplin-notesnook-memos-standard-notes"
affiliate: true
cta: true
---

Notes are the one category where "just use the cloud" feels almost impossible to escape. Evernote, Notion, Obsidian Sync, Apple Notes — they all want your data on their servers, and the moment you try to leave, you discover your notes are locked in a proprietary format or a sync engine you can't run yourself.

The self-hosted crowd has four serious answers, and they're all open source: **Joplin**, **Notesnook**, **Memos**, and **Standard Notes**. The problem is that "self-hosted notes" is a deceptively hard problem. It's not enough to run a server — the sync has to be *reliable* on iOS and Android, the mobile app has to not suck, and the encryption has to actually work without making sync fragile.

I've run all four on my Proxmox homelab. Here's the honest breakdown, scored for the person who wants their notes on their own box and their phone at the same time.

## The One Question That Matters

Before the comparison, let's name the real pain point, because it's the thing every generic listicle skips:

> **Which one syncs reliably to iOS and Android without a cloud account, and without corrupting your notes when two devices edit at once?**

That's the whole game. A notes app that only works on desktop is a diary, not a notes system. And a sync engine that drops edits or creates duplicate notes is worse than no sync at all. Everything below is scored against that question.

## The Four Contenders

**Joplin** — the veteran. Markdown notes, optional end-to-end encryption, a mature plugin ecosystem, and a self-hostable sync server. Native apps on every platform. The "boring but reliable" choice.

**Notesnook** — the privacy-first newcomer. End-to-end encryption *on by default* (not optional), a clean modern UI, and a self-host path that's newer but improving fast. The "I want E2E without thinking about it" choice.

**Memos** — the lightweight one. A single Go binary backed by SQLite, deployable in 30 seconds, with a Google-Keep-style interface. No native mobile app (it's a PWA), but the API is clean and it's the easiest thing to self-host by a mile.

**Standard Notes** — the encrypted classic. E2E encryption, a long track record, and native apps. But self-hosting it is genuinely involved — it's not one container, it's a small fleet of services.

## The Scored Comparison

| | Joplin | Notesnook | Memos | Standard Notes |
|---|---|---|---|---|
| **Sync reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Mobile app quality** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ (PWA) | ⭐⭐⭐⭐ |
| **Self-host difficulty** | ⭐⭐⭐⭐ (easy) | ⭐⭐⭐ (moderate) | ⭐⭐⭐⭐⭐ (trivial) | ⭐⭐ (hard) |
| **E2E encryption** | ⭐⭐⭐⭐ (optional) | ⭐⭐⭐⭐⭐ (default) | ⭐ (none) | ⭐⭐⭐⭐⭐ (default) |
| **Plugin/extensibility** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ (API) | ⭐⭐⭐ (extensions) |
| **Best for** | Power users, markdown nerds | Privacy-first, zero-config E2E | Quick capture, minimalists | E2E purists with patience |

Let me unpack the scores, because the table hides the real tradeoffs.

### Sync reliability

Joplin wins here on sheer maturity. Its sync engine has been battle-tested for years across Joplin Server, Nextcloud, Dropbox, WebDAV, and S3. Conflict handling is solid — it uses a per-note revision system that rarely produces duplicates. Notesnook's sync is good but younger; it's had occasional reports of sync lag on large libraries. Memos syncs fine but it's a single-user-first design — multi-device editing is fine, but it's not built for heavy concurrent editing. Standard Notes syncs reliably but only if you've correctly wired up its multi-service backend.

### Mobile app quality

Notesnook has the best mobile experience of the four — it's genuinely polished, fast, and feels like a native app. Joplin's mobile app is functional but utilitarian; it's a markdown editor first and a pretty app second. Memos has no native app — it's a PWA, which works but lacks offline-first polish and background sync. Standard Notes' mobile app is solid but the free tier nags you toward the paid plan.

### Self-host difficulty

Memos is the clear winner — one Docker container, one SQLite file, done. Joplin Server is also easy (one container + a Postgres or SQLite backend). Notesnook's self-host is a multi-container setup (web, sync server, and a few supporting services) that's improved but still more moving parts. Standard Notes is the hardest — you're running a syncing server, an API gateway, and an auth service, and the docs assume you're comfortable wiring them together.

### E2E encryption

This is where the field splits. Notesnook and Standard Notes encrypt *by default* — you don't have to opt in, and the server never sees your plaintext. Joplin's E2E is real but *optional* — you have to enable it per-notebook, and if you forget, your notes sync in plaintext. Memos has no E2E encryption at all — it's a self-hosted tool where the threat model is "you trust your own server," which is fine for a homelab but worth knowing.

## The Winner (for most homelabbers): Joplin

If you want one answer, it's **Joplin**. It's the best balance of mature sync, native apps, a real plugin ecosystem, and an easy self-host path. The E2E encryption is optional rather than default, but you can enable it and it works.

Here's a working Docker Compose stack for Joplin Server:

```yaml
version: "3.8"

services:
  joplin-db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: joplin
      POSTGRES_PASSWORD: change-me-strong-password
      POSTGRES_DB: joplin
    volumes:
      - ./joplin-db:/var/lib/postgresql/data

  joplin:
    image: joplin/server:latest
    restart: unless-stopped
    depends_on:
      - joplin-db
    ports:
      - "22300:22300"
    environment:
      APP_BASE_URL: https://joplin.yourdomain.com
      APP_PORT: 22300
      DB_CLIENT: pg
      POSTGRES_PASSWORD: change-me-strong-password
      POSTGRES_DATABASE: joplin
      POSTGRES_USER: joplin
      POSTGRES_PORT: 5432
      POSTGRES_HOST: joplin-db
    volumes:
      - ./joplin-data:/home/joplin/data
```

Then in the Joplin desktop or mobile app, go to **Settings → Synchronisation → Synchronisation target → Joplin Server**, and point it at `https://joplin.yourdomain.com` with the email and password you set up on first login.

### The gotchas (the part tutorials skip)

1. **`APP_BASE_URL` must match your public URL exactly.** If you set it to `http://localhost:22300` and then access it via a reverse proxy at `https://joplin.yourdomain.com`, sync will fail with confusing errors. Set it to the URL your clients actually use, *before* first sync.

2. **Enable E2E encryption before your first sync, not after.** If you sync a notebook in plaintext and then enable encryption, you'll have a mix of encrypted and unencrypted notes. Enable it on a fresh notebook, set a strong master password, and *write it down* — there's no recovery if you lose it.

3. **Put Joplin Server behind a reverse proxy with HTTPS.** The mobile apps will refuse to sync over plain HTTP in many cases, and you don't want your notes (even encrypted) traversing the internet in cleartext.

4. **Don't run Joplin Server and the Joplin app on the same device with the same port.** The server binds 22300; if you're also running the desktop app locally, there's no conflict, but if you're port-forwarding, make sure your router isn't already using it.

## When to Pick Something Else

**Pick Notesnook** if you want E2E encryption *without* having to think about it, and you value a polished mobile app over a plugin ecosystem. Its self-host is more moving parts, but the default-on encryption is the real differentiator.

**Pick Memos** if you want the absolute simplest thing that works — a quick-capture inbox for ideas, links, and snippets. It's a single container, it's fast, and the API means you can pipe things into it from scripts. Just know it's PWA-only and has no E2E.

**Pick Standard Notes** if you're an E2E purist who's comfortable running a multi-service backend and doesn't mind the free-tier upsell. It's the most "serious" encryption story, but you'll earn it with setup time.

## The Bottom Line

Self-hosted notes are a solved problem in 2026 — you just have to pick the right tradeoff. Most homelabbers should start with **Joplin** (mature sync, native apps, easy self-host, optional E2E). If privacy is your #1 concern and you want it on by default, **Notesnook** is the one to watch. If you want a 30-second deploy and don't need E2E, **Memos** is a delight.

The point is the same one I keep making across this site: your notes are the one dataset you'll still care about in ten years. Don't leave them on someone else's server when running your own is this easy.

---

*Want the rest of your self-hosted stack? Check out [Vaultwarden for passwords](/blog/2026-04-19-vaultwarden-self-hosted-password-manager/), [Immich for photos](/blog/2026-06-17-immich-photo-management-homelab/), and [self-hosted RSS](/blog/2026-09-06-self-hosted-twitter-nitter-xcancel/) to round out the "own your data" cluster.*
