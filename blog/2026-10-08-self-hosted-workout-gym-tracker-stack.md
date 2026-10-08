---
layout: post.njk
title: "Ditch Strava/Hevy: The Self-Hosted Workout & Gym Tracker Stack"
date: 2026-10-08
description: "I deleted Strava and Strong from my phone. Here's the honest look at the four real open-source options — openGym, wger, FitTrackee, and self-hosted GPS activity tracking — scored for workout logging, progressive overload, mobile app quality, and whether you actually own your training data."
tags: ["strava", "hevy", "strong", "self-hosted", "fitness", "health", "workout", "gym", "opengym", "wger", "fittrackee", "homelab", "docker", "comparison"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-08-self-hosted-workout-gym-tracker-stack/"
affiliate: true
cta: true
---

Your training log is arguably the most personal dataset you never think about owning. It knows your body better than your doctor's chart — every rep, every set, every kilogram you've ever moved, every run you've ever logged. And yet most of us hand it to Strava or Hevy without a second thought, where it becomes training data for *their* features and *their* social graph, not yours.

I've been self-hosting everything else — passwords, notes, photos, music, my budget — so when I looked at my phone and saw Strava and Strong sitting there, the question was obvious: *why is my fitness data the one thing I still rent?*

Here's what I found. The self-hosted fitness vertical is real, it's maturing fast, and for the devhandbook crowd (people who already run a homelab) it's an under-served corner that's genuinely worth a weekend of setup. This is the honest breakdown of the four serious options, scored for the person who wants their training data on their own box *and* an app they'll actually use in the gym.

## The One Question That Matters

Every generic "best self-hosted fitness app" listicle skips the real pain point, so let me name it:

> **Which one actually logs your workouts, tracks progressive overload, and has a mobile app that doesn't make you want to throw your phone across the squat rack?**

That's the whole game. A fitness tracker where you hand-type every set into a clunky web form is a chore you'll abandon in two weeks — the exact same way you abandoned that paper logbook in high school. Everything below is scored against that question: *can I track a workout faster than I can forget it?*

## The Four Contenders

**Strava / Strong / Hevy** — the baseline. Polished, social, mobile-first, and your data lives on their servers. This is the thing you're trying to replace.

**openGym** (941⭐) — the new kid with momentum. A self-hosted gym *and* body-weight tracker, clean modern UI, Docker-first, and genuinely pleasant to use. The one that made me sit up and pay attention.

**wger** — the veteran. Open source since 2014, a full workout manager with exercise database, routines, nutrition tracking, and a REST API. The "serious, battle-tested" choice.

**FitTrackee** — the runner's answer. A self-hosted GPS activity tracker (think self-hosted Strava for runs, rides, and hikes) with maps, statistics, and a focus on your GPS tracks actually being *yours*.

## The Scored Comparison

| | openGym | wger | FitTrackee | Strava/Hevy (baseline) |
|---|---|---|---|---|
| **Focus** | Gym + bodyweight | Full workout manager | GPS activities (run/ride) | Social fitness platform |
| **Progressive overload** | Good | Excellent | N/A (distance/pace) | Good |
| **Mobile app** | Good (PWA) | Fair (PWA, no native) | Good (PWA) | Excellent (native) |
| **Exercise database** | Built-in | Huge (thousands) | N/A | Built-in |
| **Self-host difficulty** | Easy (Docker) | Easy (Docker) | Easy (Docker) | N/A (SaaS) |
| **GPS / maps** | No | No | Yes | Yes |
| **Cost** | Free | Free | Free | $80–$100/yr |

## The Winner (for the gym crowd): openGym

If you're lifting weights or doing bodyweight work, **openGym** is the one that finally got me to delete Strong. It's a self-hosted gym and body-weight tracker that does the one thing a training log has to do — make logging a set feel effortless — and it does it with a clean, modern UI that doesn't feel like a decade-old admin panel.

What sold me: it's Docker-first (one container, one volume, up in two minutes), it tracks progressive overload properly (it remembers your last session so you can see what you did last time and beat it), and the PWA installs to your home screen so it *feels* like a native app in the gym. It's the closest thing this space has to a "just works" drop-in replacement.

Here's the working Docker Compose stack:

```yaml
services:
  opengym:
    image: ghcr.io/skydive241/opengym:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./opengym-data:/app/data
```

One container, one volume. Open `http://your-server:3000`, create your account, and start logging. Put it behind your reverse proxy with HTTPS so the PWA installs cleanly on your phone.

### The gotchas (the part tutorials skip)

1. **It's young, and it's honest about it.** openGym is under active development and moving fast. The core loop — log a workout, track the weights, see the trend — is solid, but expect occasional rough edges and features still landing. If you want something that's been stable for a decade, that's wger's lane (below).

2. **No native app — it's a PWA.** Like most self-hosted tools, openGym ships a progressive web app, not a native iOS/Android build. In practice it's fine (add to home screen, it's full-screen), but if you live in a native app with offline sync, this is the downgrade to expect.

3. **HTTPS is non-negotiable for the mobile experience.** The PWA needs to be served over HTTPS to install and work reliably. Your reverse proxy (Caddy, Nginx, Traefik) with a Let's Encrypt cert is a prerequisite, same as every other self-hosted app on this site.

4. **Back up the volume.** Your entire training history is one directory. A nightly restic snapshot is your entire disaster-recovery plan. You don't want to lose three years of PRs to a dead disk.

## When to Pick wger Instead

**Pick wger** if you want the *serious*, battle-tested option. It's been open source since 2014, which in self-hosted-fitness years is an eternity. It comes with a genuinely huge exercise database (thousands of exercises, categorized and searchable), full routine planning, weight tracking, and — the part the power users love — a REST API so you can script against your own training data.

The tradeoffs: the UI is more utilitarian than openGym's, the mobile experience is a PWA with no native app, and it's more of a "workout *manager*" than a slick logger. It's the tool you pick when you want depth and longevity over polish.

```yaml
services:
  wger:
    image: wger/server:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      DJANGO_SECRET_KEY: change-me-to-a-long-random-string
      DJANGO_DEBUG: "false"
    volumes:
      - ./wger-data:/home/wger/static
      - ./wger-media:/home/wger/media
```

## The Runner's Answer: FitTrackee

For the cardio crowd, **FitTrackee** is the self-hosted Strava replacement. It imports your GPS activities (GPX/TCX files), renders them on maps, tracks distance/pace/elevation, and — critically — your tracks stay *yours*. No social feed mining, no "your friends beat you" notifications, no paywall on your own history.

The honest catch: it doesn't do live tracking from a phone the way Strava does (you record your run with a GPS device or app, then import the file), and it's not a social network. But if what you actually want is "my runs, my maps, my stats, on my server," it delivers exactly that with a clean interface.

```yaml
services:
  fittrackee:
    image: fittrackee/fittrackee:latest
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      SECRET_KEY: change-me-to-a-long-random-string
      DATABASE_URL: postgresql://fittrackee:changeme@db:5432/fittrackee
    depends_on:
      - db
    volumes:
      - ./fittrackee-data:/opt/fittrackee/data
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: fittrackee
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: fittrackee
    volumes:
      - ./fittrackee-db:/var/lib/postgresql/data
```

## The Bigger Point: Fitness Is the Under-Served Vertical

Here's why I think this matters for the devhandbook audience specifically. We've spent years self-hosting the *obvious* things — passwords, notes, photos, media, finance. Those verticals are crowded now; there are five mature options for each and a million blog posts comparing them.

Fitness and health is different. It's the dataset you'll *still care about in twenty years* (your body is the one project you can never abandon), it's deeply personal, and the self-hosted options are just now crossing the threshold from "technically works" to "actually pleasant to use." openGym crossing 900 stars is the signal — this is the same moment Immich was at two years ago, and look where photo self-hosting is now.

If you run a homelab, you already have the server. The marginal cost of adding a workout tracker is ten minutes and a few hundred megabytes. The upside is ownership of the one logbook that follows you for the rest of your life.

## What You Give Up vs. Strava/Hevy

Let me be honest about the tradeoffs, because this is where self-hosted fitness either sticks or fails:

- **You lose the social graph.** Strava's kudos and leaderboards are genuinely fun, and there's no self-hosted replacement for "your friends can see your run." If the social layer is why you use it, self-hosting won't scratch that itch.
- **You lose the native-app polish.** PWAs are good, but they're not Strava's native app. If you live in the mobile experience, this is the biggest downgrade.
- **You lose "it just works" GPS recording.** FitTrackee needs a separate recording step (GPS device or app, then import). It's friction Strava doesn't have.
- **You gain ownership.** Your training data, your server, your rules. No price hikes, no data mining, no "we're sunsetting the free tier."
- **You gain a skill.** Running your own fitness stack is the same muscle as running Vaultwarden or Immich — and it compounds with everything else on this site.

## The Bottom Line

Self-hosted fitness is a solved-enough problem in 2026, and it's a fresher, more interesting vertical than the crowded fields we've already covered. Most gym-goers leaving Strong/Hevy should start with **openGym** (clean, easy, progressive overload done right). If you want depth and longevity, **wger** is the battle-tested choice. And runners who want their tracks back should look at **FitTrackee**.

The point is the same one I keep making across this site: your training log is the one dataset you'll still care about in twenty years. Don't leave it on someone else's server — and don't pay $100 a year for the privilege — when running your own is this easy.

---

*Want the rest of your self-hosted stack? See [Vaultwarden for passwords](/blog/2026-04-19-vaultwarden-self-hosted-password-manager/), [self-hosted notes](/blog/2026-09-09-self-hosted-notes-joplin-notesnook-memos-standard-notes/), [self-hosted budgeting](/blog/2026-09-11-self-hosted-budgeting-actual-budget-firefly-iii-ynab/), and [self-hosted music](/blog/2026-04-22-self-hosted-music-streaming/).*
