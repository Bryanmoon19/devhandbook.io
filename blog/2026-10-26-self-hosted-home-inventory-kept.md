---
layout: post.njk
title: "Self-Hosted Home Inventory & Asset Tracking with Kept: Know What You Own Before You Need It"
date: 2026-10-26
description: "kept, the AI-assisted self-hosted inventory, crossed 300 GitHub stars in about two months — and it has essentially no competition in the homelab niche. Here's why a 3D-mapped, QR-labeled inventory of everything you own is the missing half of your insurance prep, how to deploy it in Docker in minutes, and how it pairs with a cost calculator to answer the one question every renter and homeowner dreads: what is this actually worth?"
tags: ["kept", "inventory", "home-inventory", "asset-tracking", "insurance", "self-hosted", "homelab", "docker", "mcp", "ai", "paperless-ngx", "home-assistant", "qr-code", "restic"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-26-self-hosted-home-inventory-kept/"
affiliate: false
cta: true
---

Here's a question I want you to actually answer, right now, without looking anything up: **if your house burned down tonight, could you list every thing you own, where it was, and what it cost?**

Not "the big stuff." Everything. The power supplies in the drawer, the camera lenses in the closet, the box of cables in the garage, the NAS with its drives, the server that you've spent two years and a nontrivial amount of money turning into a homelab. If you're anything like me, the honest answer is no — you'd remember the laptop, the TV, and the guitar, and you'd *forget about half of everything else*, which is precisely how insurance claims get shorted by thousands of dollars you'll never get back.

Insurance is one of those things that only matters in the worst possible moment, and by then it's too late to have been prepared. The advice is always the same and always unhelpful: "take photos of everything, keep receipts, walk the house with a camera." Nobody does it. Nobody *maintains* it. The photos end up scattered across a phone and a cloud drive and six receipts in an email inbox, and when the adjuster asks for a list, you rebuild it from memory under stress, and you lose.

This week there's a project that finally makes this a solved, self-hosted problem, and it's blown up in a way that tells me a lot of other homelabbers had the same itch. **`kept`** — a self-hosted, AI-assisted inventory of everything you own and where it is — crossed **300 GitHub stars in about two months**, and it sits in a niche with essentially zero competition. That's a signal worth paying attention to.

This post is the homelab angle on Kept: what it actually is, why it hit, how to deploy it in Docker in minutes, and — the part I care about most — how it pairs with a cost calculator to turn your "pile of stuff" into a number you can defend to an insurance adjuster.

---

## The Problem Kept Solves (and Why It Has No Competition)

Let me be precise about what's weird here, because it's the reason this project matters.

There are *dozens* of mature, battle-tested self-hosted tools for every other corner of the homelab. Media? Jellyfin, Plex, Navidrome. Photos? Immich. Documents? Paperless-ngx. Passwords? Vaultwarden. Monitoring? Uptime Kuma, Beszel. The list is long, and I've written about most of it on this site.

But **home inventory** — the thing you own, where it lives, what it's worth, when the warranty expires, who you lent the drill to — has been a genuine dead zone. The few tools that existed were either abandoned, half-built, or aimed at warehouse inventory management rather than *your house*. For a niche that every single homeowner, renter, and homelabber has a real, painful need for, the pickings were shockingly thin.

Kept walked into exactly that vacuum, and the traction shows it. ~300 stars in ~2 months, an AGPL-3.0 TypeScript monorepo, a proper website, docs, a Helm chart, signed releases with cosign verification, and a roadmap that's being actively worked. This isn't a weekend toy that hit the front page once — it's a real project that found an empty room and moved in.

The pitch, in one sentence from their own README: *"Homes, garages and storage units; the rooms, shelves and boxes inside them; the things inside those, with receipts, manuals, warranties and history."* That's the whole point, and it's a thing almost nobody else is doing well.

---

## What Kept Actually Is

Before I get to the deploy, let me be concrete about what you're installing, because "inventory app" undersells it by a lot. Kept is a full-stack self-hosted application with a genuinely ambitious feature set:

- **The 3D location map.** This is the standout. Every location is a 3D map — floors, rooms, shelves, boxes — and each thing is one tap away from where it physically is. You arrange it yourself or let Kept lay it out. It sounds gimmicky until you realize it's the difference between "the HDMI cable is *somewhere in the house*" and "it's in `Home › Office › Desk drawer › Cable box`, top tray." That spatial path is the entire reason the app is useful.
- **Capture with AI.** Photograph a thing, a receipt, a label, or a whole room, and your AI provider suggests the details — you confirm them. Kept is provider-agnostic: OpenAI, Anthropic, Google, OpenRouter, Groq, or anything OpenAI-compatible like a local Ollama. No cloud account, no telemetry, and if you'd rather not, you just type the fields yourself. The AI is optional, and nothing leaves your server unless you turn it on.
- **Labels and QR codes.** Every box gets a short ID and a QR code you print on label sheets. Scan one to open that box, run a scan session to count a shelf, pack a box, or move a pile in one go. This is the feature that makes the inventory *actually stay current* — which is the thing every other approach fails at.
- **The household.** Shared locations with roles, lending (who has the drill, and did they return it), kits that go out and come back as a unit, stocktakes, schedules, warranties, and paperwork. Reminders in-app, by mail, by push, and in a calendar feed.
- **Insurance report.** A first-class insurance report, because that's the killer use case. Everything you've logged, with values, receipts, and photos, exported as something you can hand to an adjuster.
- **Moving house.** Numbered boxes, a label and contents sheet for each, tracked in the van, unpacked by scanning.
- **Vehicles and machines.** Readings, services, fuel, running costs — because a homelabber's "assets" include the car and the power tools.
- **AI assistant and MCP server.** Ask in plain words, changes wait for your confirmation, and Claude / ChatGPT / any MCP client connects at `/mcp`. That last bit is what makes this feel *of this moment* — it's an inventory that an AI agent can query and update, with your approval as the gate.
- **Backups you can read.** Nightly restic backups to a directory, S3, or SFTP — and each backup has a copy that opens in a browser *without Kept*, so your insurance evidence survives even if the app itself doesn't.

That's a serious feature set, and it's the reason this isn't just "a spreadsheet with a web UI." It's the difference between *logging* what you own and *actually being able to find and prove* what you own.

---

## The Insurance Angle (the Part That Actually Matters)

I want to spend a moment on this, because it's the thing that converts Kept from "neat homelab toy" into "thing that will save you real money someday."

When you make an insurance claim for a loss — fire, flood, theft — the burden of proof is on **you**. The adjuster isn't going to take your word that you had a $1,400 camera body and a $600 lens. They're going to ask for evidence: proof you owned it, proof of what it cost, and proof of what it was. Every item you can't substantiate is money you don't recover. And the cruel part is that the moments when you'd be *most* motivated to document everything are exactly the moments when you're too stressed, too tired, and too busy to do it properly.

Kept flips that by making the documentation *continuous* instead of *retroactive*:

- **Receipts, manuals, and warranty cards** attach to the *thing*, not to a folder in your email. Paperless-ngx links directly, so the receipt for the NAS lives next to the NAS in Kept.
- **Photos and serial numbers** get captured at the moment of entry, when the thing is new and you have it in hand — not after it's gone.
- **The insurance report** turns the whole inventory into a single, defensible document: everything, with value, photos, and paperwork, ready to hand over.
- **The value is a number, not a guess.** And this is where the calculator pairing comes in.

### Pairing Kept with a cost calculator

Knowing *what* you own is half the job. Knowing *what it's worth* is the other half, and it's the half people consistently get wrong — especially homelabbers, whose "stuff" is a mix of new gear, secondhand finds, and things whose value only makes sense in context.

The honest approach is two tools, doing two jobs:

1. **Kept** tells you *what you have and where it is* — the inventory itself, with receipts and serial numbers and photos.
2. **A cost calculator** tells you *what it cost and what it's worth* — the actual spend on the hardware, the power, the recurring costs, and what it would take to replace it.

On this site, the [Homelab Cost Calculator](/homelab-cost-calculator/) does the second job for the hardware half of your life: true total cost of ownership — hardware, power draw, internet, and a comparison against what the equivalent cloud hosting would run you. It's the "what did I actually spend on this server" number. Feed that into Kept's value fields for the NAS, the server, the drives, and the networking gear, and suddenly your insurance report isn't "a computer, some drives" — it's a line item with a defensible replacement cost attached.

The workflow I'd suggest: **inventory in Kept, price in the calculator, and let the insurance report be the merge.** Log the thing in Kept with its receipt and photo; compute its real cost in the calculator; enter that as the value. When you need the report, it's all there, already substantiated. You never do the "walk the house with a camera at 2 AM" panic because you've been doing it continuously, in five-minute increments, for months.

---

## Deploying Kept in Docker

Deployment is refreshingly clean for a project this young — a single Compose file, no repo clone, no hand-rolled passwords. Here's the whole thing.

### Prerequisites

- Docker with Compose v2
- A machine with at least **2 GB of RAM and 2 CPU cores** (a Mac mini, a small Proxmox LXC, or any modest homelab box is plenty)
- A hostname if you want printed labels to carry a clean URL (an IP address works, but a name like `kept.home.arpa` beats it)

### The quick start

```sh
mkdir kept && cd kept
curl -fsSLO https://raw.githubusercontent.com/keptinventory/kept/v1.13.0/compose.yaml
docker compose run --rm init
docker compose up -d
```

Let me walk through what each of those does, because it's genuinely well-designed:

1. **`compose.yaml`** is the whole stack in one file — no clone, no manual setup. Database, a one-shot bootstrap that generates the DB logins and passwords, a one-shot `migrate`, and Kept itself on port `8080` (`KEPT_HTTP_PORT` changes it).
2. **`init`** asks what address you'll open Kept at, writes `.env`, and prints a **setup code**. That code is your bootstrap secret.
3. **First run:** open the address, enter the setup code, create the first account — it becomes the instance admin. Then keep the keys *off* the server: `docker compose exec kept kept admin recovery-kit` prints the recovery kit you store somewhere safe.

### HTTPS (you'll want it)

The camera, the installed phone app, push notifications, and location all need HTTPS. One extra profile handles it:

```sh
docker compose --profile https up -d
```

That adds Caddy with a certificate for `KEPT_DOMAIN`, generated from the Caddyfile in `docker/caddy/`. If you're already running a reverse proxy or [Cloudflare Tunnel](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/) in front of your services, you can terminate TLS there instead — the point is just that the browser and the phone need a secure origin.

### Backups and verification

Two things worth doing from day one, and both are built in:

- **Backups:** nightly, encrypted, to a directory, S3, or SFTP. Configure it once and forget it — your insurance evidence depends on it.
- **Verify the image:** `cosign verify --key cosign.pub <image>:<version>` against the `cosign.pub` key from the repo. For a tool you're trusting with a complete manifest of everything you own, verifying the image you run is cheap diligence, not paranoia.

---

## What Kept Plays Nicely With

Kept is designed to slot into a stack you probably already run, which is exactly what you'd want from a homelab tool. The integrations are the good kind — two-way, and with the tools that are already popular:

- **Home Assistant** — a HACS custom repository integration, so your inventory can surface in your dashboards and your automations can read it.
- **Paperless-ngx** — receipts, manuals, and warranty cards link directly to things. This is the natural pairing: Paperless is your document store, Kept is your inventory, and they reference each other.
- **Imports** — from Homebox (the closest prior thing to Kept) and CSV, so you're not starting from zero if you already tried another tool.
- **Notifications** — ntfy, Telegram, Slack, Discord, Matrix, Signal, email, and webhooks, for the reminders and lending pings.
- **MCP** — the `/mcp` endpoint for Claude and ChatGPT, which is where the "AI-assisted" promise gets interesting in a way I'll come back to.

The theme across all of it: Kept assumes you already have a homelab, and it *composes* with it rather than trying to replace it.

---

## The MCP Angle (Why This Feels Like 2026)

The single most interesting thing in Kept, to me, is the MCP server — and it's the feature that tells you *when* this project was built.

MCP (Model Context Protocol) is how AI agents talk to external tools, and Kept ships a server at `/mcp` that lets Claude, ChatGPT, or any other MCP client query and — with your approval — update your inventory. The demo in their README is Claude Code adding a TV with its serial number, correctly placed in `Home › Living room`, after a plain-English request.

That's a big deal for a specific reason: **the hard part of an inventory was never the database. It was the data entry.** Nobody wants to type in forty boxes of cables. The AI capture already helps by photographing a room and suggesting details, but the MCP server goes further — it means the agent you're already running can *maintain* the inventory conversationally, and the changes wait for your explicit OK before they land.

For a homelabber who's already got an AI coding assistant or an agent wired up (and this site has written a *lot* about that), Kept is one of the few genuinely useful things you can point an agent at that isn't a codebase. It's your stuff, as a queryable, updatable graph, with a human approval gate on every write. That's the part that feels like it couldn't have shipped two years ago.

---

## The Honest Downsides (Because It's Two Months Old)

I refuse to write a cheerleading post, and a project this young deserves its caveats stated plainly.

- **It's young, and it's AGPL.** Two months old means rough edges, and AGPL-3.0 means you should read what that implies if you ever plan to modify and *distribute* it. For self-hosting your own household inventory, AGPL is essentially irrelevant — but it's worth knowing the license you're installing, especially for a tool you're giving a full manifest of your possessions.
- **2 GB minimum is real.** It's not a 64 MB unprivileged container. Kept is a full-stack app (TypeScript, a database, the 3D map, AI capture), and it wants a couple gigs and a couple cores. That's fine on a Mac mini or a small LXC, but it's not a "throw it on the old Raspberry Pi" install. There's an open issue about running comfortably on 2 GB, which tells you they know it's a constraint they're working on.
- **The AI capture is only as good as your provider.** The AI-assist is genuinely useful, but if you point it at a small local Ollama model, expect more manual correction than with a frontier cloud model. That's not Kept's fault — it's the honest reality of local models — but "AI-assisted" doesn't mean "zero data entry" on modest hardware.
- **HTTPS is not optional for the good features.** Camera, phone app, push, and location all want a secure origin. That's a one-line `--profile https` or a reverse-proxy config, but it's a step you can't skip if you want the phone experience, which is where the app really shines (capture happens in the garage, not at the desk).
- **It's another thing to back up and patch.** This is the standing homelab tax on everything, but it's worth saying explicitly because the *stakes* are higher: this is the one service where losing the data isn't just annoying, it's exactly the thing you built it to prevent. Configure the restic backups on day one, not "someday."

None of these are reasons not to use it. They're reasons to use it *deliberately* — with backups on, HTTPS on, and an understanding of what "two months old" means.

---

## The Verdict

The homelab niche has a long-standing pattern: a category of real need sits empty, someone ships a focused, self-hosted tool into it, and it takes off because the demand was always there and simply had nowhere to go. Kept is that story for home inventory, and the ~300 stars in ~2 months are the market confirming the obvious: **everyone has stuff, and almost no one has a good way to know what it is, where it is, and what it's worth.**

The insurance angle is the thing that turns it from a curiosity into something you should actually deploy. Insurance is the rare domain where *continuous, low-effort documentation* pays off in hard dollars at a moment you can't predict — and Kept is the first self-hosted tool I've seen that makes that documentation something you'll actually keep up with, because the 3D map, the QR labels, the AI capture, and the phone app make it almost pleasant instead of a chore.

Pair it with a cost calculator for the "what's it worth" half, and you've closed the loop: **know what you own (Kept), know what it cost (calculator), and be able to prove both (insurance report).** That's the thing you'll be grateful for not at setup time, but the night the worst happens and you're the one who can hand over a complete, substantiated list while everyone else is reconstructing from memory.

It's two months old, it wants 2 GB, and it won't be the last word in the niche it just defined. But it's the right tool today, in a category that was empty yesterday, and for a self-hosted homelab that's about as strong an endorsement as any new project can earn.

**Resources:**
- [Kept (GitHub)](https://github.com/keptinventory/kept)
- [Kept documentation](https://keptinventory.info/)
- [Try Kept in your browser](https://keptinventory.info/try/kept/)
- [Kept install guide (Docker Compose)](https://keptinventory.info/install/compose/)
- [Kept MCP clients](https://keptinventory.info/users/mcp-clients/)
- [Homelab Cost Calculator (the companion tool)](https://devhandbook.io/homelab-cost-calculator/)

---

*Self-hosting your home inventory, or still on the "photos in a folder" method? Got a Kept setup or an insurance-report workflow worth sharing? Drop it in the [Discord](https://discord.gg/selfhosted) — always curious how people are turning their pile of stuff into a number they can defend.*
