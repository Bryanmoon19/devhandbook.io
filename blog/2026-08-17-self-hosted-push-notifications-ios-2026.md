---
layout: post.njk
title: "Self-Hosted Push Notifications on iOS in 2026: The Decision Matrix"
date: 2026-08-17
description: "Every homelabber running ntfy, Gotify, or Home Assistant eventually slams into the same wall: iOS doesn't do Web Push the way Android does. But the landscape shifted in 2026 — a self-hosted web push Cloudflare Worker hit 76 points on HN, and Apple finally opened the door. Here's the honest decision matrix: ntfy vs Gotify vs web-push vs the HA Companion app."
tags: ["self-hosted", "push-notifications", "ios", "ntfy", "gotify", "web-push", "home-assistant", "cloudflare-workers", "homelab", "apns"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-17-self-hosted-push-notifications-ios-2026"
---

# Self-Hosted Push Notifications on iOS in 2026: The Decision Matrix

There's a moment every homelabber hits, usually around 11pm, usually right after they've wired up their third self-hosted service. They want a notification when a backup fails, when a drive hits 90% full, when the garage door opens. They install ntfy or Gotify, it works beautifully on their Android phone, and then they pick up their iPhone and… nothing.

iOS has been the wall for self-hosted push notifications for years. Android lets any app register a persistent connection and receive pushes from anywhere. iOS doesn't. Apple routes *everything* through APNs (Apple Push Notification service), and for a long time that meant you either paid for a third-party relay, or you used the one blessed workaround — the Home Assistant Companion app — or you gave up and used email.

But 2026 changed the calculus. A post titled *"Self-hosted web push Cloudflare Worker, works on iOS"* hit 76 points on Hacker News, and it pointed at something genuinely new: **iOS 16.4+ finally supports Web Push for installed web apps.** That single change cracked open a door that had been bolted shut for a decade.

This isn't another "install ntfy" walkthrough. This is the decision matrix I wish I'd had — the four real options for getting self-hosted push notifications onto an iPhone in 2026, what each one actually costs you, and which one you should pick based on what you're trying to do.

## Why iOS Is Different (And Why It Finally Changed)

To understand the options, you have to understand the constraint. On Android, a push notification is just a message over a persistent connection. Any app can hold a socket open and receive whatever you send it. That's why ntfy and Gotify are trivial on Android — they're just a server and a client that talk to each other.

iOS doesn't work that way. Apple's battery management kills background connections aggressively, so the only reliable way to wake an app is through **APNs** — Apple's own push infrastructure. Every push to an iPhone, no matter who sends it, has to flow through Apple's servers. That's not a technical limitation you can route around; it's a policy baked into the OS.

For years, that meant self-hosters had exactly three choices:

1. **Use a third-party relay** that holds an APNs certificate and forwards your notifications (ntfy's paid tier, Pushover, etc.)
2. **Use the Home Assistant Companion app**, which is a real App Store app with its own APNs integration
3. **Give up on push and use email/SMS**

Then iOS 16.4 shipped Web Push in March 2023, and it took a couple of years for the self-hosting community to really exploit it. The trick: **if you "Add to Home Screen" a web app, that web app can receive Web Push notifications** — and Web Push doesn't require APNs at all. It uses the same VAPID/Web Push protocol that browsers use, which means you can self-host the entire thing with a Cloudflare Worker and zero Apple involvement.

That's the 76-point HN post. And it's the reason this decision matrix exists now.

## The Four Contenders

Let me lay out the field. These are the four ways to get a self-hosted push notification onto an iPhone in 2026, and they optimize for very different things.

### ntfy — the "just works, mostly" default

[ntfy](https://ntfy.sh) is the most popular self-hosted push server, and for good reason. It's a single Go binary, it has a dead-simple HTTP API (`curl -d "backup failed" ntfy.example.com/alerts`), and it has first-class apps for Android and iOS.

The catch is the iOS app. ntfy's iOS app works, but it has a fundamental constraint: **to receive pushes reliably in the background, it needs to go through ntfy's own relay (ntfy.sh) or a self-hosted APNs bridge.** The free ntfy.sh relay works but means your notifications transit a third party. The self-hosted APNs bridge requires you to set up your own APNs certificate — which is doable but is exactly the kind of fiddly Apple-provisioning work most people are trying to avoid.

**Best for:** people who want the easiest possible setup and don't mind the free relay, or who are willing to do the APNs bridge work for full self-hosting.

### Gotify — the Android-first purist

[Gotify](https://gotify.net) is the other big name, and it's beloved in the self-hosting community for being simple, lightweight, and fully self-contained. It's a single binary with a clean web UI and a simple REST API.

The problem: **Gotify has no official iOS app.** The project has been explicit about this — the maintainer built it for Android and has no interest in the APNs dance. There are third-party iOS clients, but they're community-maintained and hit the same background-delivery wall. On iOS, Gotify is effectively a web-app-only experience, which means you're back to the Web Push question anyway.

**Best for:** Android-first homelabs, or iOS users who are fine checking notifications in a web app rather than getting true background pushes.

### Web Push (self-hosted, via a Cloudflare Worker) — the 2026 newcomer

This is the option the HN post is about, and it's the most interesting development in years. The idea: **run a tiny Web Push server (often a Cloudflare Worker) that speaks the standard Web Push protocol, and subscribe to it from an iOS web app you've added to your Home Screen.**

Because iOS 16.4+ supports Web Push for installed web apps, this works *without* APNs, *without* a third-party relay, and *without* any Apple developer account. You self-host the entire notification pipeline. The HN post that hit 76 points is a concrete, working implementation of exactly this.

The trade-offs are real, though. Web Push on iOS has quirks: the web app has to be installed to the Home Screen (not just open in Safari), the notification experience is slightly less polished than a native app, and you're building a small amount of glue code rather than installing a turnkey server. But for the "I want it fully self-hosted and I don't want to touch APNs" crowd, it's the first genuinely good answer.

**Best for:** people who want true end-to-end self-hosting, are comfortable with a bit of glue code, and don't mind the Home Screen web-app workflow.

### Home Assistant Companion — the "I already run HA" answer

If you run Home Assistant, you already have the best iOS push solution on the market, and you might not even realize it. The [Home Assistant Companion app](https://companion.home-assistant.io) is a real, App Store-distributed iOS app with proper APNs integration, and it can receive push notifications for *anything* — not just HA automations.

The killer feature: **HA Companion exposes a webhook that any service can POST to.** You can have ntfy, Gotify, a cron job, a monitoring tool, or a random shell script all funnel notifications into HA, and HA Companion delivers them to your iPhone with full native reliability. It's the bridge that makes every other self-hosted tool work on iOS.

The trade-off is that it's not *fully* self-hosted in the purist sense — the APNs leg still goes through Apple (and, depending on your setup, HA's optional cloud relay). But it's the most reliable, most polished, and lowest-effort path to native iOS notifications, and it's free.

**Best for:** anyone already running Home Assistant, or anyone who wants native-quality iOS notifications without building anything.

## The Decision Matrix

Here's the whole thing in one table. This is the part to bookmark.

| | **ntfy** | **Gotify** | **Web Push (Worker)** | **HA Companion** |
|---|---|---|---|---|
| **iOS native app** | ✅ (needs relay/APNs) | ❌ (no official app) | ❌ (web app) | ✅ (App Store) |
| **True background push** | ✅ (via relay) | ❌ | ✅ (installed web app) | ✅ |
| **Fully self-hosted** | ⚠️ (relay is third-party) | ✅ | ✅ | ⚠️ (APNs leg is Apple) |
| **APNs / Apple account needed** | ⚠️ (for self-hosted bridge) | ❌ | ❌ | ❌ (app handles it) |
| **Setup difficulty** | Easy | Easy | Medium (glue code) | Easy (if you run HA) |
| **Notification polish** | Good | N/A on iOS | Decent | Excellent |
| **Resource footprint** | Tiny (single binary) | Tiny (single binary) | Tiny (Worker) | Needs HA running |
| **Best for** | Easiest path | Android-first | Purist self-hosting | HA users, best UX |

There's no single winner. The right answer depends entirely on what you already run and how much "self-hosted" purity you're willing to trade for reliability.

## How to Choose (The Honest Flowchart)

Here's the decision logic I'd actually walk someone through, in order:

**1. Do you already run Home Assistant?**
If yes, stop. Use the HA Companion app. It's the best iOS push experience in self-hosting, it's free, and it takes ten minutes to wire up. You can still run ntfy or Gotify *behind* it if you want their APIs, but HA Companion is your delivery layer.

**2. Do you need true background push, or is "check the app" fine?**
If you're okay opening an app to see notifications, Gotify's web UI (or any web app) is fine, and you can skip the whole APNs/Web Push question. But most people want the phone to buzz in their pocket, which means you need one of the real delivery mechanisms.

**3. Are you a purist about self-hosting?**
If "no third party touches my notifications" is a hard requirement, you have two real options: the self-hosted APNs bridge (ntfy supports this) or the Web Push Worker approach. The Web Push Worker is the more modern answer and avoids Apple provisioning entirely, but it means living with a Home Screen web app.

**4. Do you want the least effort possible?**
If you just want it to work and don't care about the relay, use ntfy with the free ntfy.sh relay. It's the fastest path from zero to "my iPhone buzzes when my backup fails," and you can always graduate to the self-hosted bridge later.

**5. Are you building something custom?**
If you're a developer building a product or a bespoke notification pipeline, the Web Push Worker is the most interesting option — it's the only one that gives you full control of the entire stack with no Apple account and no third-party relay.

## The Web Push Worker, In Practice

Since the Web Push approach is the new thing and the least documented, let me give you the shape of it. The core insight is that Web Push is a *standard* — it's the same protocol Chrome and Firefox use — and iOS 16.4+ speaks it for installed web apps.

The minimal setup looks like this:

1. **A Web Push server** — often a Cloudflare Worker that holds your VAPID keys and stores subscriptions. It exposes two endpoints: one to subscribe (the browser sends a `PushSubscription`), and one to send (you POST a message, it fans out to all subscribers).

2. **A web app** — a tiny HTML page with a service worker that calls `registration.pushManager.subscribe()`. The user opens it in Safari, taps "Add to Home Screen," and grants notification permission.

3. **A sender** — anything that can POST to your Worker's send endpoint. A cron job, a monitoring tool, a shell script, ntfy, whatever.

The VAPID keys are the only "secret" — they're a public/private keypair that identifies your push server to the browser. You generate them once, store them in the Worker's environment, and you're done. No Apple developer account, no APNs certificate, no $99/year.

The HN post that hit 76 points is a complete, working implementation of this, and it's worth reading if you go this route. The main gotchas to know up front:

- **The web app must be installed to the Home Screen.** Web Push doesn't work from a plain Safari tab on iOS. This is the single most common "it doesn't work" complaint.
- **Notification actions are limited.** You get a title, a body, and a tap-through URL. No rich media, no custom buttons, no interactive replies. If you need those, you need a native app (HA Companion).
- **You're maintaining a small amount of code.** It's not a turnkey server like ntfy. It's maybe 100 lines of Worker + service worker, but it's *your* code to keep running.

## The Bottom Line

Self-hosted push notifications on iOS stopped being a lost cause in 2026. The wall that used to force everyone into third-party relays or the HA Companion app now has a real, self-hosted alternative in Web Push — and the HN post that hit 76 points is the proof that the community has figured out how to make it work.

But "possible" and "right for you" are different things. Here's the short version:

- **You run Home Assistant?** Use the Companion app. Done. It's the best iOS push experience in self-hosting, full stop.
- **You want the easiest path and don't mind a relay?** Use ntfy with the free relay.
- **You're a purist who wants zero third parties?** Use the Web Push Worker. It's the 2026 answer, and it's genuinely good.
- **You're Android-first?** Gotify is still great — just know it's not a real iOS solution.

The thing that changed isn't that Apple suddenly embraced self-hosting. It's that the community found a way through the APNs wall using a standard Apple already supported. That's the whole story of self-hosting in 2026, really: the walls don't come down, but the routes around them keep getting better.
