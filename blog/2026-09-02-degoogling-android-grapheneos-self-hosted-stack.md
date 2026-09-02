---
layout: post.njk
title: "De-Googling Your Android Phone: GrapheneOS + a Self-Hosted Contacts, Calendar, and Photos Stack"
date: 2026-09-02
description: "GrapheneOS is having a moment — the Motorola partnership, the airport-wipe story, PayPal blocking users. But nobody's written the end-to-end guide that pairs GrapheneOS with your own contacts, calendar, and photos server. This is that guide: the capstone that ties together de-Cloudflare, de-Google-location, and self-hosted calendar into one working phone."
tags: ["grapheneos", "android", "de-google", "degoogle", "privacy", "self-hosted", "homelab", "contacts", "calendar", "photos", "immich", "radicale", "davx5", "caldav", "carddav", "pixel", "motorola", "security"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-09-02-degoogling-android-grapheneos-self-hosted-stack"
---

GrapheneOS is having a moment, and it's not the quiet kind.

In the last few months it's hit the news three separate times for three very different reasons: a [partnership with Motorola](https://grapheneos.org/articles/motorola-partnership) to ship hardened phones, a viral story about a GrapheneOS user whose phone [wiped itself at an airport](https://grapheneos.org/features#duress-password) (the duress-password feature working exactly as designed), and PayPal [blocking GrapheneOS users](https://grapheneos.org/articles/paypal) from logging in because the OS is "too secure" for their fraud heuristics.

The result is a wave of people — normal people, not just privacy maximalists — suddenly asking the same question: *"Can I actually run my phone without Google?"*

The answer is yes. But here's the part nobody's written down: **installing GrapheneOS is the easy half. The hard half is what you do after.** A phone with no Google account is a phone with no contacts, no calendar, and no photo backup — unless you build your own.

That's what this post is. It's the capstone that ties together the pieces I've been writing about all year — [de-Cloudflare](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/), [de-Google-location](/blog/2026-08-23-google-location-history-self-host/), and [self-hosted calendar](/blog/2026-06-26-self-hosted-calendar-tools-homelab/) — into one working phone that doesn't phone home to Mountain View.

## Why GrapheneOS, and Why Now

Let me be clear about what GrapheneOS is and isn't, because there's a lot of half-remembered confusion floating around.

GrapheneOS is a **privacy- and security-hardened Android** built on the Android Open Source Project (AOSP). It's not a fork that strips Google and calls it a day — it's a from-the-ground-up hardening project that adds real security features on top of a de-Googled base:

- **No Google Play Services** by default. No silent telemetry, no location pings, no account requirement to use the phone.
- **A hardened kernel and memory allocator** that make whole classes of exploits dramatically harder.
- **Sandboxed Google Play** — if you *want* a Google app, it runs in a sandbox with no more privileges than any other app, instead of the god-mode access Play Services gets on stock Android.
- **Duress password** — the feature behind the airport story. A separate PIN that, when entered, wipes the device. It's for the scenario where someone forces you to unlock your phone.

The Motorola partnership matters because it's the first time GrapheneOS has shipped on hardware that isn't a Google Pixel. That's a signal the project is maturing past "enthusiast ROM" into something a normal person can buy and use.

And the PayPal story matters for a different reason: it's proof that GrapheneOS's security is *real enough to trip fraud detection.* When a payment processor blocks you because your device doesn't leak the fingerprint it expects, that's not a bug — that's the OS doing its job.

## The Honest Reality Check

Before I hand you a stack, let me be honest about the trade-offs, because "de-Google your phone" is sold as a clean win and it isn't quite:

- **You lose some apps.** Anything that hard-requires Play Services (some banking apps, some games, some Google-first apps) won't work, or works only through sandboxed Play. Check your must-have apps *before* you flash.
- **You become your own IT department.** No Google means no Google backup. If your phone dies, your data is wherever *you* put it. That's the point — but it's also the responsibility.
- **Notifications are a known pain point.** Without Play Services' push channel, some apps need a self-hosted push relay (I covered this for iOS [here](/blog/2026-08-17-self-hosted-push-notifications-ios-2026/); Android has its own story with UnifiedPush).

None of this is a dealbreaker. It's just the honest cost of admission. The payoff is a phone that doesn't report your location, your contacts, your calendar, or your photos to an advertising company.

## The Stack, At a Glance

Here's the whole thing in one picture. This is what we're building:

| Need | Google's answer | Your answer |
|------|----------------|-------------|
| OS | Stock Android + Play Services | **GrapheneOS** |
| Contacts | Google Contacts | **Radicale** (CardDAV) |
| Calendar | Google Calendar | **Radicale** (CalDAV) |
| Photos | Google Photos | **Immich** |
| Sync on device | Google account | **DAVx⁵** |
| Location history | Google Timeline | **OwnTracks / self-hosted** |
| App store | Play Store | **F-Droid + Aurora** |

The beautiful part: **Radicale handles both contacts and calendar** with one tiny container. You don't need a sprawling stack. One CalDAV/CardDAV server, one photo server, and a sync app on the phone. That's the whole thing.

## Part 1: Flash GrapheneOS

I'm not going to re-derive the install guide — the [official one](https://grapheneos.org/install/web) is excellent and kept current. But here's the shape of it, because the *order* matters:

1. **Buy a supported device.** A Google Pixel (6 or newer) is the classic choice; the Motorola partnership is adding options. Check the [supported devices list](https://grapheneos.org/faq#supported-devices) before you buy anything.
2. **Unlock the bootloader.** This wipes the phone, so do it on a fresh device.
3. **Flash via the web installer.** The web USB installer is the easiest path — it downloads the right build and flashes it for you.
4. **Relock the bootloader.** This is the step people skip, and it's the one that matters. A relocked bootloader is what makes GrapheneOS's verified boot actually mean something.

The whole thing takes about 20 minutes if you've done it before, maybe an hour the first time. The install is not the hard part.

## Part 2: Stand Up Radicale (Contacts + Calendar)

This is where the self-hosting begins, and it's the piece I've already [written about in depth](/blog/2026-06-26-self-hosted-calendar-tools-homelab/). The short version: **Radicale is the answer.** It's a tiny Python CalDAV/CardDAV server that does contacts and calendar in one container, has been around since 2008, and never crashes.

Here's the Docker Compose I run:

```yaml
services:
  radicale:
    image: tomsquest/docker-radicale:latest
    container_name: radicale
    restart: unless-stopped
    ports:
      - "5232:5232"
    volumes:
      - ./radicale/data:/data
      - ./radicale/config:/config
    environment:
      - TZ=America/New_York
```

The config file (`/config/config`) is where you set up auth. For a family setup, you want per-user accounts so everyone's contacts and calendars stay separate:

```ini
[auth]
type = htpasswd
htpasswd_filename = /config/users
htpasswd_encryption = bcrypt

[server]
hosts = 0.0.0.0:5232

[storage]
filesystem_folder = /data/collections
```

Create users with `htpasswd -B /config/users bryan` and you're done. Each user gets their own address book and calendar, and you can create shared calendars for the family.

**Why Radicale over Nextcloud?** Because Nextcloud is a kitchen sink — gigabytes of PHP, a database, Redis, and upgrade anxiety — when all you need is CalDAV and CardDAV. Radicale is one container, one config file, and it just works. If you *already* run Nextcloud, use its Calendar and Contacts apps. If you're starting fresh, don't drag in a whole collaboration platform for two sync endpoints.

## Part 3: Stand Up Immich (Photos)

Google Photos is the hardest thing to replace, and [Immich](/blog/2026-06-17-immich-photo-management-homelab/) is the tool that finally makes it possible. It's a self-hosted photo platform with automatic backup from your phone, face recognition, and a web UI that genuinely rivals Google Photos.

```yaml
services:
  immich-server:
    image: ghcr.io/immich-app/immich-server:release
    container_name: immich_server
    volumes:
      - ./immich/upload:/usr/src/app/upload
      - /etc/localtime:/etc/localtime:ro
    env_file:
      - .env
    ports:
      - "2283:2283"
    depends_on:
      - redis
      - database
    restart: unless-stopped

  redis:
    image: redis:6.2-alpine
    container_name: immich_redis
    restart: unless-stopped

  database:
    image: tensorchord/pgvecto-rs:pg14-v0.2.0
    container_name: immich_postgres
    env_file:
      - .env
    volumes:
      - ./immich/pgdata:/var/lib/postgresql/data
    restart: unless-stopped
```

The Immich mobile app backs up your photos automatically, and — critically for a de-Googled phone — it doesn't need Play Services. You install it from F-Droid or sideload the APK, point it at your server, and it just works.

## Part 4: Wire the Phone to Your Servers

This is the step that makes it all come together, and it's the one most guides skip. You've got servers running. Now the phone needs to talk to them.

### DAVx⁵ for contacts and calendar

[DAVx⁵](https://www.davx5.com/) is the Android app that syncs CalDAV and CardDAV. Install it from F-Droid, add your Radicale server, and your contacts and calendar appear in the native Android apps — no Google account required.

The setup is two accounts (or one, if you point both at the same Radicale URL):

- **CardDAV URL:** `https://your-server:5232/` (contacts)
- **CalDAV URL:** `https://your-server:5232/` (calendar)

DAVx⁵ handles the rest. Your phone's Contacts and Calendar apps now read from *your* server, not Google's.

### Immich app for photos

Install the Immich app, log in with your server URL and credentials, and enable automatic backup. Your photos flow to your own storage instead of Google's.

### F-Droid and Aurora for apps

You need an app store. [F-Droid](https://f-droid.org/) is the open-source store — everything on it is free and auditable. [Aurora Store](https://auroraoss.com/) is a Play Store client that lets you install Play apps anonymously, without a Google account. Between the two, you cover almost everything.

### Location history (optional, but worth it)

I wrote a whole post about [Google deleting your location history](/blog/2026-08-23-google-location-history-self-host/) and how to self-host it. The short version: [OwnTracks](https://owntracks.org/) logs your location to your own server, and you can visualize it with a tool like the google-timeline-visualizer I covered. It's the last piece of the "Google knows where I am" puzzle.

## Part 5: The De-Cloudflare Tie-In

Here's where this post connects to the [de-Cloudflare runbook](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/) I published a couple weeks ago.

If you're de-Googling your phone, you're already thinking about who holds your data. But a lot of people do the phone part and then expose their Radicale and Immich servers through Cloudflare Tunnels — which means they've traded Google for Cloudflare without noticing. Your contacts and photos are now flowing through *another* third party's infrastructure.

The honest answer is that Cloudflare Tunnels are convenient, and for a lot of people they're fine. But if your goal is "my data stays mine," the consistent move is to expose your servers through a path you control — a WireGuard tunnel, Tailscale/Headscale, or a reverse proxy on a VPS you own. I covered the [Headscale self-hosted Tailscale](/blog/2026-08-24-headscale-self-host-tailscale/) option, and the de-Cloudflare runbook has the full migration checklist.

The point isn't that Cloudflare is evil. It's that **de-Googling is a mindset, not a checklist.** If you're going to do it, do it all the way — otherwise you've just moved your data from one big company to another.

## What I'd Do Differently Next Time

I've now run this stack for long enough to have opinions:

1. **Set up Radicale *before* you flash the phone.** The worst moment is a freshly-de-Googled phone with no contacts and no calendar, and you're fumbling to stand up a server while your family asks why you can't see the shared grocery list. Build the server first, then flash.
2. **Test your must-have apps on a spare device first.** I assumed my banking app would work through sandboxed Play, and it mostly did — but one app flat-out refused. Know your app situation before you commit your daily driver.
3. **Backups are now your job.** Google used to do this silently. Now you need to back up your Radicale data directory and your Immich library. I use [restic](/blog/2026-08-14-docker-backup-playbook-restic-dockstash/) pointed at the same NAS I migrated in [the TrueNAS post](/blog/2026-09-01-truenas-core-to-scale-proxmox-sso-migration/). Set it up on day one, not month three.
4. **Notifications need a plan.** Without Play Services, push notifications for some apps break. UnifiedPush + a self-hosted relay (ntfy) is the fix, but it's a separate project. Budget time for it.

## The Bottom Line

De-Googling your Android phone is not a single weekend project — it's a stack, and it's a stack I've now written about piece by piece all year. This post is the capstone that ties it together:

- **GrapheneOS** replaces the OS and the Google account.
- **Radicale** replaces Google Contacts and Google Calendar.
- **Immich** replaces Google Photos.
- **DAVx⁵** wires the phone to your servers.
- **OwnTracks** replaces Google Timeline.
- **Your own tunnel** replaces the Cloudflare dependency.

None of it is hard in isolation. The hard part is the *consistency* — actually following through on the "my data stays mine" claim instead of stopping halfway.

But here's the thing that surprised me: once it's set up, it's not a burden. It's quieter. No "Google wants to access your location" prompts. No "we've updated our privacy policy" emails. No ads that know what you talked about at dinner. Just a phone that does what you tell it, and servers that hold your data because *you* put it there.

If GrapheneOS's moment has you curious, the install is the easy part. The stack is the real project — and now you've got the whole thing in one place.

---

*Running GrapheneOS? Hit a wall with DAVx⁵ or Immich on a de-Googled device? I'd genuinely like to hear how it went — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*Related reading: [De-Cloudflare: The Self-Hosted Trust Runbook](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/), [Google Is Deleting Your Location History — Self-Host It](/blog/2026-08-23-google-location-history-self-host/), [Self-Hosted Calendar Tools for Homelabbers](/blog/2026-06-26-self-hosted-calendar-tools-homelab/), and [Immich: The Self-Hosted Google Photos Alternative](/blog/2026-06-17-immich-photo-management-homelab/).*
