---
layout: post.njk
title: "Google Is Deleting Your Location History — Self-Host It Before It's Gone"
date: 2026-08-23
description: "Google retired the web version of Timeline and moved your location history to on-device storage — and if you didn't export it in time, it's already gone. A Kotlin app called google-timeline-visualizer just blew past 2,600 stars by turning your exported Timeline.json into animated travel videos. Here's what actually happened to your data, how to get it back, and how to self-host it so Google never holds the only copy again."
tags: ["google-timeline", "location-history", "self-hosted", "privacy", "google-maps", "timeline", "data-export", "homelab", "teslamate", "location-data", "google-takeout", "data-sovereignty"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-23-google-location-history-self-host"
affiliate: true
cta: true
---

There's a quiet panic happening right now, and it's not on the front page of Hacker News. It's in the support threads, the Reddit posts, and the "where did my Timeline go?" searches that spike every time someone opens Google Maps and realizes a decade of their life is missing.

The short version: **Google killed the web version of Timeline, and if you didn't export your location history before the deadline, it's gone.** Not hidden. Not "we'll restore it if you ask nicely." Deleted.

And this week, a Kotlin app called [google-timeline-visualizer](https://github.com/mahlernim/google-timeline-visualizer) blew past 2,600 stars by doing something Google no longer does — turning your exported `Timeline.json` into an animated travel video, entirely on your own device. It's trending for a reason: people are realizing, too late, that the only copy of their location history was the one Google was about to throw away.

This post is about what actually happened, how to get your data back if you still can, and how to make sure you never depend on Google to hold the only copy of your own movement again.

## What Actually Happened to Google Timeline

Let me get the timeline of the Timeline right, because there's a lot of half-remembered confusion floating around.

Google Timeline — the feature that used to be called **Location History** — was the map that showed everywhere you'd been, every day, for as long as you'd had it turned on. For a lot of people that's ten-plus years of data: every trip, every commute, every city you visited, every restaurant you forgot you went to.

In late 2023, Google announced a major change: Timeline would **move from the cloud to your device.** The pitch was privacy — "your location data stays on your phone, encrypted, under your control." The reality was a hard deadline: the web version of Timeline would be shut down, and any location history that hadn't been migrated to a device would be **deleted.**

Google extended the deadline a couple of times, but the end result was the same. If you didn't open Google Maps, follow the migration prompt, and save your data before the cutoff, your web Timeline was wiped. No recovery. No "we kept a backup just in case."

The part that stings is how easy it was to miss. The prompt lived inside Google Maps, buried under your profile picture → Settings → Personal content. If you didn't open Maps during the migration window, or you dismissed the notification thinking you'd do it later, you never saw it again. And "later" turned into "never."

### Why This Is a 2026 Pain Point, Not a 2024 One

The deadline passed a while ago. So why is this trending *now*?

Because people don't check their Timeline every day. They check it when they want to remember something — a trip, an anniversary, the name of that place they stayed in 2019. And it's only when they go looking that they discover the data is gone.

That's the cruel part of this kind of deprecation. The people who cared enough to export their data did it during the window. The people who didn't think about it — who assumed Google would just keep their history forever, because Google keeps *everything* — are finding out months later, one at a time, that the assumption was wrong.

The `google-timeline-visualizer` spike is the leading indicator. It's a tool for people who *did* export their data and now want to do something with it. But for every person who has a `Timeline.json` to feed it, there are ten who are just now realizing they should have exported one.

## The Tool That's Trending: google-timeline-visualizer

Let's talk about the app itself, because it's genuinely good and it's the reason this topic is hot right now.

[google-timeline-visualizer](https://github.com/mahlernim/google-timeline-visualizer) is a Kotlin app (MIT-licensed) that takes your exported `Timeline.json` and turns it into an **animated travel video** — a map that traces your route over time, rendered as an MP4 you can watch or share. It's the kind of thing Google Timeline used to do natively, back when it was a web product with a "year in review" feature.

What makes it notable for the self-hosting crowd:

- **It runs entirely on-device.** On Android it's a native app; on iPhone there's a [web app](https://ahn-lab.org/google-timeline-visualizer/) that processes the file in Safari without uploading anything. Your location data never leaves your device.
- **It's not on Google Play yet.** You install the APK directly from the GitHub releases page, which is a whole separate conversation about sideloading and trust (I've written about [iOS sideloading workflows](/blog/2026-08-17-self-hosted-push-notifications-ios-2026/) before — same muscle).
- **It handles the restore case.** If your older trips disappeared after a phone swap or a Maps reinstall, the app points you at Google's encrypted Timeline backup and a restoration guide.

The app is a symptom of the larger shift. When Google deprecated the web Timeline, it didn't just delete a feature — it deleted the *interface* people used to look at their own history. Tools like this are filling that gap, one `Timeline.json` at a time.

## How to Get Your Data Back (If You Still Can)

Before you do anything else, check whether your data is actually gone. There are a few paths, and they're worth trying in order.

### 1. Check Your Device Timeline

Open Google Maps → tap your profile picture → **Settings → Personal content → Timeline.** If your history is there, you're fine — but **export it now.** Don't wait. The whole point of this post is that "I'll do it later" is how people lose a decade of data.

### 2. Export Your Timeline.json

The export path differs by platform, and it's easy to get wrong:

- **On Android:** it's in the *phone's* Settings app, not Maps. **Settings → Location → Location services → Timeline → Export Timeline data.** Save the `Timeline.json` somewhere you'll actually find it.
- **On iPhone:** **Google Maps → profile picture → Settings → Personal content → Export Timeline data.**

That `Timeline.json` file is the thing you want to keep. It's your entire location history in one portable, self-contained file. Back it up like you'd back up anything irreplaceable.

### 3. Restore a Missing Timeline

If older trips vanished after changing phones or reinstalling Maps, there may be an **encrypted Timeline backup** still sitting in your Google account. The visualizer app links to a [restoration guide](https://github.com/mahlernim/google-timeline-visualizer/blob/main/docs/restore-google-maps-timeline.md), and Google's own [Timeline Help](https://support.google.com/maps/answer/6258979) covers the menu paths. Restore in Maps first, *then* export a fresh JSON.

### 4. Google Takeout, as a Last Resort

If you had Location History enabled historically, run a [Google Takeout](https://takeout.google.com/) export and look for location data. Takeout is the nuclear option — it dumps everything — but it's worth checking whether any location records survived in your account even if the Timeline UI is empty.

The uncomfortable truth: **if none of these turn up data, it's gone.** Google deleted it on schedule, and there's no support ticket that brings it back. That's the lesson to internalize, and it's the reason the rest of this post matters.

## Self-Host It: Never Let Google Hold the Only Copy Again

The deeper problem here isn't Google Timeline specifically. It's the pattern: **you trusted a free cloud service to be the sole custodian of data you cared about, and the service changed the terms.**

The fix isn't to be angry at Google. It's to stop depending on any single provider to hold the only copy of your own data. For location history, that means three things.

### 1. Export on a Schedule

Set a recurring reminder — monthly or quarterly — to export your `Timeline.json` and store it somewhere you control. It's a five-minute task. The file is small. The cost of not doing it is a decade of memories.

### 2. Store It Where You Control It

Drop the export into your own storage — a NAS, a self-hosted Nextcloud, a Synology, whatever you run. If you're already running a homelab, this is trivial. If you're not, this is a good excuse to start (my [Proxmox NAS guide](/blog/2026-08-07-proxmox-nas-truenas-anas-turnkey/) covers the turnkey path).

The point is that the file lives on *your* hardware, under *your* backup policy, not behind a Google account that can change its mind.

### 3. Visualize It Yourself

This is where `google-timeline-visualizer` earns its stars. Once you have the `Timeline.json`, you can render it into something you actually *enjoy* — an animated map of a trip, a year-in-review video, a keepsake. The data stops being a dormant file and becomes something you use.

## The TeslaMate Connection: Location Data Done Right

I've written before about [running TeslaMate on Proxmox](/blog/teslamate-proxmox-lxc/) to log my Tesla's trips, charging, and efficiency. And there's a direct parallel here that's worth making explicit.

TeslaMate is what Google Timeline *should* have been: **a self-hosted location logger where you own the database.** It pulls telemetry from the Tesla API and stores it in your own PostgreSQL instance. The data lives on your hardware. Google can't deprecate it, can't delete it, can't change the terms on it. It's yours because it's on your disk.

The contrast is the whole argument in one example:

| | Google Timeline | TeslaMate |
|---|---|---|
| **Where the data lives** | Google's cloud (now your device, if you migrated) | Your PostgreSQL, on your hardware |
| **Who controls retention** | Google, on a schedule you don't set | You, forever |
| **What happens on deprecation** | Data deleted if you miss the window | Nothing — it's already yours |
| **Export format** | `Timeline.json` (if you act in time) | Raw SQL, Grafana dashboards, CSV |

The lesson generalizes. For *any* data you care about — location, photos, music, documents — the question isn't "which cloud service is best." It's "do I hold the only copy, or does someone else?" If someone else does, you're one deprecation notice away from losing it.

## The Bottom Line

Google Timeline's web deprecation is a case study in a specific kind of loss: the loss that happens *quietly*, on a schedule, to people who assumed the default was "keep it forever."

The people who exported their data are fine — they're the ones making travel videos with `google-timeline-visualizer` right now. The people who didn't are finding out one at a time, months later, that a decade of their movement is unrecoverable.

Here's the compressed version, the card to stick on your monitor:

1. **Check your Timeline right now.** If it's there, export it today.
2. **Save the `Timeline.json` somewhere you control** — your NAS, not Google's cloud.
3. **Set a recurring export reminder.** Quarterly is plenty.
4. **If it's already gone, try the restore path** — encrypted backup, then Takeout — before you accept the loss.
5. **Self-host the data you care about.** TeslaMate for your car, your own storage for your location history, your own database for everything else.

Google didn't delete your location history out of malice. It deleted it because, to Google, it was a deprecated feature. To you, it was a decade of your life. The difference between those two framings is exactly why you should hold the only copy.

---

*Did you lose your Google Timeline, or did you export in time? What are you doing with your `Timeline.json`? I'd love to hear — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [running TeslaMate on Proxmox](/blog/teslamate-proxmox-lxc/), [self-hosting your own email](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail/), and the [Proxmox NAS guide](/blog/2026-08-07-proxmox-nas-truenas-anas-turnkey/).*
