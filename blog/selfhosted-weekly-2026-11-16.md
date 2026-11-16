---
layout: post.njk
title: "Self-Hosted This Week: Rebuilding the Serverless Cloud, One Runtime at a Time — November 10–16, 2026"
date: 2026-11-16
description: "OpenWorkers brings Cloudflare Workers home in Rust, Celld un-Durable-Objects Durable Objects, a $10 map stack replaces Mapbox, a 15MB app does Netflix-and-Spotify, and someone roots their smart bed. This week's roundup."
tags: ["selfhosted", "weekly", "homelab", "roundup", "cloudflare", "serverless", "maps", "media", "self-hosting", "ai"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-11-16"
---

Last week the story was about the *foundation* — a decade-old SSH bug waking up, Ubuntu stalling on a critical patch, the trust layer under everything you run. This week, the self-hosting crowd got busy doing something more constructive: **rebuilding the cloud on their own terms.**

The through-line this week wasn't any single tool. It was a direction. Cloudflare built a brilliant set of serverless primitives — Workers, Durable Objects, KV, R2 — and then the open-source world looked at them and said, *"nice, we'll take those, thanks."* OpenWorkers recreates the Workers runtime in Rust. Celld recreates Durable Objects as a self-hosted daemon. Talorys puts a whole personal AI agent inside *your* Cloudflare account so the vendor holds no state of its own. And while that was happening, the quieter corners of the homelab kept chipping away at the other big cloud taxes: map tiles, media streaming, and the smart bed that stops working when AWS sneezes.

Here's what caught my eye from November 10–16, 2026.

---

## 1. OpenWorkers — Self-Hosted Cloudflare Workers, Written in Rust

**What it is:** [OpenWorkers](https://openworkers.com/introducing-openworkers) is a new open-source serverless platform — 500 points on Hacker News — that runs the Cloudflare Workers programming model (fetch handlers, KV, SQL, storage, cron) on your *own* infrastructure. JavaScript and TypeScript in V8 isolates, Rust as native WebAssembly components, all MIT licensed end-to-end: runtime, API, and dashboard. It's in public beta.

**Why it matters:** This is the clearest signal yet of a shift that's been building for a while: **the serverless abstraction is being decoupled from the vendor that invented it.** Cloudflare's Workers API is genuinely good — the `fetch` handler model is clean, the edge-first DX is comfortable, and a generation of developers learned it. OpenWorkers' bet is that the *interface* is worth keeping while the *billing and the lock-in* are not. For self-hosters, that's the whole game: you get the ergonomics of a managed serverless platform, but the box, the data, and the cold-start latency all belong to you. It's also a vote of confidence in Rust as the substrate for infrastructure — fast warm requests, millisecond cold starts, no per-invocation metering.

**The takeaway:** "Self-hosted serverless" used to be a contradiction in terms. OpenWorkers is making it a product category.

[**Introducing OpenWorkers →**](https://openworkers.com/introducing-openworkers)

---

## 2. Celld — Distributed Durable Objects You Run Yourself

**What it is:** [Celld](https://github.com/denoland/celld) is an open-source daemon (286 points) that runs a full Cloudflare Workers application on your own machines — Workers, Durable Objects, KV, Queues, D1, R2, Workflows, cron triggers, and static assets — deployed from the `wrangler.json` you already have. Each object is a "cell": a named server with its own SQLite database, with long-term state stored in your S3-compatible bucket. No serving control plane, no consensus service. An inactive cell costs almost nothing.

**Why it matters:** Durable Objects are Cloudflare's genuinely clever answer to stateful serverless — little stateful islands that make realtime collaboration and per-object consistency sane. Celld takes that exact model and makes it *portable*. The interesting bit is the architecture: every node embeds V8, executes Wrangler bundles, and a simple conditional bucket write grants ownership of a cell. There's no coordinator to run, no etcd to babysit. For a self-hoster, that's the dream — the distributed-systems power without the distributed-systems operational burden. It pairs naturally with OpenWorkers: between the two of them, the "you have to stay on Cloudflare" argument loses most of its teeth.

**The takeaway:** The stateful half of serverless just got a self-hosted exit ramp, and it doesn't require a PhD in consensus to run.

[**Celld on GitHub →**](https://github.com/denoland/celld)

---

## 3. Protomaps / PMTiles — Self-Hosting Map Tiles Just Got Cheap and Easy

**What it is:** [PMTiles](https://bruceroettgers.eu/blog/protomaps/) is a map-tile format that ships as a *single file*, served via HTTP Range requests, deployable to any storage bucket. Bruce Röttgers' writeup (294 points) walks through getting real map data, dropping the file onto Bunny.net, and embedding it in a page — no tile server, no PostGIS, no Mapbox bill.

**Why it matters:** Maps are one of those things everyone quietly assumed you had to rent. Mapbox charges $5 per 1,000 map loads past the free tier; Google's terms are a maze. The moment a project gets popular, the map bill becomes the reason it can't survive going viral. PMTiles collapses the entire stack — the tile server, the caching layer, the CDN config — into "upload one file." For self-hosters it means a genuinely *free, self-owned* map layer for the dashboard, the family locator, the "where did I park" app, the homelab network map. It's the kind of quiet un-bundling that quietly kills a big SaaS line item.

**The takeaway:** Maps stopped being a vendor you owe money to and became a file you own. That's a self-hosting win with real dollar signs attached.

[**Self-hosting map tiles with Protomaps →**](https://bruceroettgers.eu/blog/protomaps/)

---

## 4. HolyArrs — a 15 MB Self-Hosted Netflix *and* Spotify for Your Media Server

**What it is:** [HolyArrs](https://github.com/HolyArrs/HolyArrs) is a single self-hosted app for shows, movies, music, *and* downloads — the whole "Netflix and Spotify in one" pitch, at a 15 MB footprint, which earned 170 points as a Show HN. It's built by the *arr-adjacent crowd's favorite aesthetic: one binary, one app, no constellation of services.

**Why it matters:** The self-hosted media world has long been a family of specialists — Sonarr for TV, Radarr for movies, Lidarr for music, Prowlarr for indexers, Jellyfin for playback, each its own container, its own config, its own opinion about port numbers. HolyArrs is the counter-movement: *one app that does the whole job.* That resonates with a real segment of self-hosters who are tired of orchestrating a dozen services just to watch a show. The 15 MB number is the emotional hook — it's a statement that you don't need a Kubernetes cluster to run your own media empire. Whether it displaces the specialist stack is an open question, but the *impulse* it represents — consolidation, simplicity, "just one thing to run" — is very much alive.

**The takeaway:** The pendulum in self-hosted media is swinging back toward "one app to rule them all." Some of us are ready.

[**HolyArrs on GitHub →**](https://github.com/HolyArrs/HolyArrs)

---

## 5. Talorys — a Personal AI Agent That Lives in *Your* Cloudflare Account

**What it is:** [Talorys](https://github.com/rociiu/talorys) is a free, open-source personal AI assistant (331 points) that runs entirely inside your *own* Cloudflare account — one command (`npx create-talorys@latest`), free-tier friendly, single-user, no telemetry. It chats, remembers, manages tasks and notes, and runs scheduled reminders and routines, with **no server, database, or account operated by the Talorys developers.**

**Why it matters:** This is a clever twist on the "self-hosted AI agent" genre. Most personal-agent projects ask you to spin up a box and babysit a model. Talorys instead *exploits* the free tier of a giant you already trust with DNS — and keeps all your state inside your own account, so the developer holds nothing. It's "self-hosted" in the sense that matters most to privacy: *the vendor can't see your data because there's no vendor.* It also quietly makes the argument that the cheapest self-hosting plan in 2026 is the free tier of a platform you're already paying nothing for. For the homelab crowd, it's a reminder that "own your data" and "run your own server" are no longer synonyms — sometimes the smart move is to own the account and let someone else run the infra.

**The takeaway:** You don't always need your own server to own your data. Sometimes you just need your own account and an exit path.

[**Talorys on GitHub →**](https://github.com/rociiu/talorys)

---

## 6. Fuzzy Canary — Fighting AI Scrapers With the Oldest Trick in the Book

**What it is:** [Fuzzy Canary](https://github.com/vivienhenz24/fuzzy-canary) (373 points) is an npm package that plants *invisible links to porn sites* in your HTML, on the theory that AI scrapers running content-safety classifiers will hit the links, trip their own safeguards, and go elsewhere. It's a defense mechanism for the self-hosted blog you'd rather not have vacuumed into a training set.

**Why it matters:** The "AI companies are scraping everything" fight is one self-hosters feel personally — your blog, your docs, your photos are the raw material. And the honest answer has been grim: robots.txt is a suggestion, IP-blocking is whack-a-mole, and there's no real enforcement. Fuzzy Canary is the *mischievous* answer: if you can't keep the scrapers out, make the content toxic to their pipelines. It's half joke, half genuine arms-race maneuver, and entirely in the spirit of the self-hosting ethos — *my site, my rules, and if your bot doesn't like what it finds, that's your bot's problem.* Whether it actually deters any scraper is beside the point; it's a reminder that the "can't win" framing is a choice, and the homelab crowd keeps choosing creative resistance over resignation.

**The takeaway:** The scraper fight isn't over, and the self-hosting side just got a lot funnier about it.

[**Fuzzy Canary on GitHub →**](https://github.com/vivienhenz24/fuzzy-canary)

---

## 7. Rooting the Eight Sleep Pod 3 — Your Bed Is Yours, Even If the Vendor Forgot

**What it is:** [Ryan Bagley's writeup](https://rb.ax/blog/rooting-the-eight-sleep-pod-3/) documents rooting his Eight Sleep Pod 3 — patching the firmware archive on the SD card to gain root on the control board, using the open-source `free-sleep` app so the bed works without the vendor's cloud.

**Why it matters:** The origin story is the kicker: in late 2025, an AWS outage left Eight Sleep customers unable to control the machine sitting *at their bedside* because the servers were thousands of miles away. A smart bed — a heating pad with a microcontroller, really — bricked by a cloud dependency. Bagley's response is the purest expression of the right-to-repair instinct this movement runs on: if the thing in your own bedroom won't work without a distant server, you take the firmware apart and make it yours. It's a small story with a huge thesis — **every "smart" device is a self-hosting opportunity waiting to happen.** Your thermostat, your bed, your car's ECU (which someone else reverse-engineered with a $3 Arduino this week). The cloud is full of things that should have been local.

**The takeaway:** Ownership isn't a legal question. It's a soldering iron and a willingness to void a warranty.

[**Rooting the Eight Sleep Pod 3 →**](https://rb.ax/blog/rooting-the-eight-sleep-pod-3/)

---

## Honorable Mentions

- **Qwen4-Max** (414 pts) — Alibaba's [latest flagship open-weight model](https://qwen.ai/blog?id=qwen4-max), with claims of 60% lower task costs. The local-LLM crowd's new benchmark to chase.
- **Moltworker** (246 pts) — [Cloudflare's own self-hosted AI agent](https://blog.cloudflare.com/moltworker-self-hosted-ai-agent/), a sign that even the vendors see the writing on the wall.
- **Universal XSS in uBlock Origin** (298 pts) — a [website-driven element picker bug](https://iter.ca/post/ubo-uxss/) in everyone's favorite blocker. Patch your extensions.
- **Eclipse Mosquitto** (88 pts) — the [open-source MQTT broker](https://github.com/eclipse-mosquitto/mosquitto) at the heart of half the homelab's IoT stack, getting a well-deserved spotlight.
- **GrapheneOS calls Linux a "human slop kernel"** (39 pts) — a [spicy security take](https://twitter.com/GrapheneOS/status/2122074518437134627) that lit up the replies, whether you agree or not.

---

## Closing Thought

Three weeks ago these roundups were about the *industry catching up* to self-hosting. Last week was about the *trust layer* getting tested. This week felt like the answer to both: **the self-hosting community stopped waiting for the cloud to be fair and started rebuilding the cloud.**

OpenWorkers and Celld didn't ask Cloudflare for a self-hosted license — they reimplemented the Workers model in Rust and V8 and handed it to you MIT-licensed. Talorys turned the free tier into a privacy play. PMTiles turned a per-load bill into a file. HolyArrs turned a constellation of containers into one 15 MB binary. And a guy rooted his own bed because a faraway server once told him he couldn't.

The pattern is the same one that's been running through this whole series: **abstraction is the cloud's product, and ownership is yours.** The cloud's cleverest primitives — serverless functions, durable objects, map tiles, media streaming, even the AI agent — all turn out to have a "run it yourself" version now, and this week that version got dramatically better. The gap between "what the cloud offers" and "what you can own" has never been narrower, and it's the self-hosting crowd closing it.

The only remaining question is the one that's always been there: how much of the stack are you willing to *actually run*, versus just admire from the front page of Hacker News? This week made the running a lot more tempting.

What did you de-cloud this week? Drop a comment — I read every one.

---

_This is a weekly series covering trending self-hosted projects, homelab tools, and open-source infrastructure. Subscribe via RSS or follow devhandbook.io for more._
