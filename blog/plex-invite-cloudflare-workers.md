---
layout: post.njk
title: "Build a Serverless Plex Invite System with Cloudflare Workers"
date: 2026-03-25
description: "Stop sharing root Plex access. Build a Telegram-powered invite flow that gives friends exactly the libraries they need — for free, no server required."
tags: ["plex", "cloudflare", "self-hosted", "telegram", "serverless", "homelab"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/plex-invite-cloudflare-workers"
---

If you run a Plex server, you've been through this. A friend asks for access. You log into the Plex dashboard, navigate to Settings → Users & Sharing, type their email, pick libraries, send the invite. Two minutes of clicking. Now multiply that by every new friend, every library change, every "can I get the kids' section too?" follow-up.

There's a better way. One that takes 15 minutes to set up, runs for free on Cloudflare, and lets your friends request access through a form while you approve from your phone.

This post walks through building exactly that — the same system I built for my own server, called **[InvitArr](https://github.com/Bryanmoon19/invitarr)**.

## The Architecture

**A Cloudflare Worker + KV + Telegram bot handles the full invite flow at zero cost, no server needed.**

The whole thing runs on **Cloudflare Workers** with **KV storage** for state. There's no database to host, no VPS to maintain, and no Docker container to keep alive. The free tier handles this easily.

Here's the flow:

```text
Friend fills out your request form
           ↓
Cloudflare Worker receives POST → validates → stores in KV
           ↓
Telegram bot sends you a notification with inline buttons
           ↓
You tap ✅ → Library picker appears (toggle each library)
           ↓
You tap 📤 Send Invite → Worker calls Plex API → restricted invite sent
```

The key detail: you control *which libraries* each person gets, per-invite, from Telegram. Not everyone needs access to your 4K encodes or your guilty-pleasure reality TV collection.

## Prerequisites

**You need a Cloudflare account, a Plex server, a Telegram account, and Node.js — nothing else.**

- A Cloudflare account (free tier is sufficient)
- Plex Media Server running somewhere
- A Telegram account (for notifications)
- Node.js installed locally (for Wrangler CLI)

## Step 1 — Create a Telegram Bot

**Message @BotFather to get a token, then @userinfobot for your Chat ID — takes 2 minutes.**

You'll need a bot to send yourself approval notifications.

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy your **bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

Next, find your own Telegram user ID. Send a message to [@userinfobot](https://t.me/userinfobot) — it'll reply with your ID. This is your `CHAT_ID` and acts as the owner allowlist. Only your Telegram account can approve requests.

## Step 2 — Get Your Plex Credentials

**Grab your Plex token from dev tools and global section IDs from the plex.tv sharing API — not local IDs.**

You need two things: your Plex auth token and your server's machine identifier.

**Plex token:** Log into [plex.tv](https://plex.tv), open dev tools, and look for `X-Plex-Token` in any API request. Or go to a library item, click the `...` menu → Get Info → View XML — the token is in the URL.

**Machine ID (server identifier):** Visit `http://YOUR_PLEX_IP:32400/identity` in a browser. You'll get an XML response with a `machineIdentifier` field.

**Library section IDs:** This is the tricky part. Plex has *local* section IDs (the ones you see in URLs) and *global* section IDs (what the sharing API actually needs). Get the global ones by visiting:

```text
https://plex.tv/api/servers/YOUR_MACHINE_ID/shared_servers
```

Look for `sectionId` values in the response. These are the IDs you'll use, formatted as `"Library Name:sectionId"` pairs:

```text
Movies:107518710,TV Shows:107518703,Music:107518712
```

## Step 3 — Set Up the Worker

**Clone InvitArr, create a KV namespace, and push your 5 secrets — no config files with credentials.**

Clone InvitArr and install dependencies:

```bash
git clone https://github.com/Bryanmoon19/invitarr.git
cd invitarr/worker
npm install -g wrangler
```

**Create a KV namespace** for storing pending invite requests:

```bash
wrangler kv namespace create invitarr
```

Copy the output ID into `wrangler.toml`:

```toml
name = "invitarr"
main = "src/index.js"
compatibility_date = "2024-01-01"

[[kv_namespaces]]
binding = "KV"
id = "YOUR_KV_NAMESPACE_ID_HERE"
```

**Set your secrets** — these live in Cloudflare's environment, not in your code:

```bash
wrangler secret put BOT_TOKEN        # Telegram bot token
wrangler secret put CHAT_ID          # Your Telegram user ID
wrangler secret put PLEX_TOKEN       # Your Plex auth token
wrangler secret put PLEX_SERVER_ID   # Your Plex machine identifier
wrangler secret put PLEX_LIBRARIES   # "Movies:107518710,TV Shows:107518703"
```

Optional but worth setting:

```bash
wrangler secret put OWNER_NAME       # "Bryan" — shown in the form
wrangler secret put SERVER_NAME      # "Moon's Media Server"
wrangler secret put ALLOWED_ORIGIN   # Your guide page domain
```

## Step 4 — Deploy

**Run `wrangler deploy` then register the Telegram webhook — your system is live immediately after.**

```bash
wrangler deploy
```

Wrangler will output your worker URL — something like `https://invitarr.YOUR_SUBDOMAIN.workers.dev`.

**Register the Telegram webhook** so your bot knows to send updates to your worker:

```bash
curl "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -d "url=https://invitarr.YOUR_SUBDOMAIN.workers.dev/telegram"
```

Your worker is now live.

## Step 5 — The Request Form

**Friends submit name + email; you get a Telegram message with ✅/❌ buttons and per-library toggles.**

The worker serves a built-in HTML request form at its root URL (`/`). You can link directly to it, or embed the form URL in a guide page for your friends.

The form collects name and email, includes a hidden honeypot field to catch bots, and sends the data to your worker. Your friend sees a confirmation screen; you get a Telegram message.

The Telegram notification looks like this:

```text
🎬 New Plex Request

👤 Jane Smith (jane@example.com)

[✅ Send Invite]  [❌ Decline]
```

Tap ✅ and a second message appears with inline toggles for each library:

```text
📚 Select Libraries for Jane Smith:

[✅ Movies]  [☑️ TV Shows]  [✅ Music]

[📤 Send Invite]  [🚫 Cancel]
```

Toggle the libraries, tap 📤 Send Invite, and Plex sends a restricted invitation to Jane's email. The KV entry expires automatically after 24 hours regardless.

## The Security Details

**Owner allowlist, rate limiting, honeypot, CORS lock, and encrypted secrets keep this safe to expose publicly.**

This was designed to be safe to deploy publicly. A few things worth noting:

**Owner allowlist:** Only Telegram users matching your `CHAT_ID` can approve requests. The library picker and Send Invite button are completely inert for anyone else.

**Rate limiting:** The worker tracks request counts per email/IP in KV and rejects repeated submissions within a time window.

**Honeypot:** The form has a hidden field that only bots fill in. Submissions with that field populated are silently rejected.

**CORS lock:** Set `ALLOWED_ORIGIN` to your guide page domain, and the worker will reject POST requests from anywhere else.

**No stored credentials:** Your Plex token and bot token live as Cloudflare secrets, encrypted at rest. They're never in your codebase or logs.

## Hosting the Guide Page

**Deploy the included guide page to Cloudflare Pages for free — gives friends better onboarding than a raw URL.**

InvitArr includes a drop-in guide page (`/guide/index.html`) that walks your friends through getting the Plex app, creating an account, and what to expect after requesting access. It supports both English and Spanish, has a dark mode, and you configure it with a single JS block at the top:

```html
<script>
const SITE_CONFIG = {
  ownerName: "Bryan",
  serverName: "Moon's Media Server",
  requestUrl: "https://invitarr.YOUR_SUBDOMAIN.workers.dev",
  // ... other settings
};
</script>
```

Host it on Cloudflare Pages (also free), GitHub Pages, or any static host. Share the guide URL instead of the raw worker URL — your friends get better onboarding, you get fewer "how do I install Plex?" questions.

```bash
# Deploy guide to Cloudflare Pages
cd invitarr/guide
npx wrangler pages deploy . --project-name invitarr-guide
```

## Costs

**This entire system costs $0/month — Workers, KV, and Pages all stay well within Cloudflare's free limits.**

**Cloudflare Workers free tier:** 100,000 requests/day. Your Plex invite volume will never touch this. Cost: $0.

**Cloudflare KV free tier:** 100,000 reads/day, 1,000 writes/day. Each invite request is 2-3 writes. Cost: $0.

**Cloudflare Pages:** Free tier covers unlimited static requests. Cost: $0.

**Total:** $0/month, forever, for a system with better UX than the Plex web dashboard.

## The Full Setup Script

**Run `setup.sh` for an interactive guided setup that handles KV, secrets, deploy, and webhook in ~5 minutes.**

If you'd rather not run commands manually, InvitArr includes a guided setup script that handles everything interactively:

```bash
git clone https://github.com/Bryanmoon19/invitarr.git
cd invitarr/worker
chmod +x setup.sh && ./setup.sh
```

It walks you through each secret, creates the KV namespace, deploys the worker, and registers the Telegram webhook. About 5 minutes end-to-end if you have your credentials ready.

## What's Next

**Jellyfin and Emby support are on the roadmap — same architecture, different API calls for the invite step.**

InvitArr currently supports Plex. Jellyfin and Emby support are on the roadmap — the architecture is the same, just different API calls for the invite step.

If you run a Jellyfin server and want to contribute or request priority support, [open an issue on GitHub](https://github.com/Bryanmoon19/invitarr/issues). Contributions welcome.

---

The source code is at [github.com/Bryanmoon19/invitarr](https://github.com/Bryanmoon19/invitarr). MIT licensed, no strings attached. If you build on it, I'd love to know.

Got questions or hit a snag? The README covers common failure modes — the most frequent one is using local library section IDs instead of global ones. If you're getting "invite sent" confirmations but friends aren't appearing in Plex, that's almost certainly the issue.
