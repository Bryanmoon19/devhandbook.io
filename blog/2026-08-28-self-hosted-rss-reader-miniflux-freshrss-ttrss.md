---
layout: post.njk
title: "Self-Hosted RSS Reader: Miniflux vs FreshRSS vs Tiny Tiny RSS (2026)"
date: 2026-08-28
description: "Your feed is an algorithm now, and it's not on your side. RSS is the antidote — a feed you actually control. Here's a hands-on comparison of Miniflux, FreshRSS, and Tiny Tiny RSS, the three best self-hosted readers, with Docker Compose for each and a decision guide for which one fits your brain."
tags: ["rss", "miniflux", "freshrss", "tt-rss", "tiny-tiny-rss", "self-hosted", "homelab", "feeds", "privacy", "docker", "reading", "open-source", "algorithm"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-28-self-hosted-rss-reader-miniflux-freshrss-ttrss"
affiliate: false
cta: true
---

# Self-Hosted RSS Reader: Miniflux vs FreshRSS vs Tiny Tiny RSS

There's a moment every self-hoster eventually hits, and it usually comes right after they've finished moving their media, their photos, and their passwords off the cloud. They look at their phone, open the app they use to "catch up on the news," and realize they have no idea why they're seeing what they're seeing.

The feed isn't chronological. It isn't complete. It's a black box that decides, on your behalf, what deserves your attention — and it's optimized for *engagement*, not for *you*.

That's the moment RSS stops being a nostalgic acronym and starts being the answer. **RSS is the antidote to the algorithmic feed.** It's a feed you subscribe to, not one that's fed to you. And in 2026, self-hosting your own RSS reader is easier than it's ever been.

This post is the comparison I wish I'd had before I spent a weekend trying the three big self-hosted readers. If you've been following my self-hosting series — the [ebook library](/blog/2026-08-25-self-hosted-ebook-library-calibre-web-kavita-komga/), the [audiobooks guide](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/), the [music stack](/blog/2026-05-16-self-hosted-music-navidrome-soulseek/) — this is the natural next piece: **owning the thing that decides what you read.**

Here's the short version, then we'll go deep.

| Tool | Best for | Language | Database | Standout feature |
|------|----------|----------|----------|------------------|
| **Miniflux** | Minimalists, keyboard nerds | Go | Postgres | Fast, no-JS, fever API |
| **FreshRSS** | Power users, self-hosted Google Reader | PHP | SQLite/MySQL/Postgres | Full-text search, extensions |
| **Tiny Tiny RSS** | Tinkerers, plugin lovers | PHP | Postgres/MySQL | Deep plugin ecosystem |

---

## The Problem: You Don't Own Your Feed Anymore

Let me name the actual pain, because it's not "I can't find an RSS app." It's that **the default way we consume information is now a product designed to keep us scrolling, not to keep us informed.**

Think about what an algorithmic feed actually is:

- **It's incomplete.** You see a curated slice, not everything. The algorithm decides what's "important," and you never see the rest.
- **It's not chronological.** The order is optimized for engagement, not for time. A three-day-old post can sit above a three-minute-old one because it's "performing better."
- **It's not yours.** You can't export it, you can't back it up, and if the platform changes its mind — or shuts down — your entire reading history vanishes.
- **It's adversarial.** The algorithm isn't neutral. It's tuned to maximize the time you spend in the app, which is not the same thing as maximizing the value you get out of it.

RSS inverts all of that. With RSS:

- **It's complete.** You subscribe to a feed, you get every post. No curation, no shadow-banning, no "we hid this from you."
- **It's chronological.** Newest first, always. You read in the order things happened.
- **It's yours.** Your subscriptions live in a file (or a database) you control. Export it, back it up, move it to another reader in five minutes.
- **It's neutral.** The only thing deciding what you see is *you*, when you subscribed to the feed.

The catch, historically, was that RSS readers were either dead (Google Reader, RIP 2013) or clunky desktop apps. But the self-hosting community has quietly built three excellent web-based readers that give you the Google Reader experience — sync across devices, keyboard shortcuts, full-text search — on hardware you own.

---

## The Three Contenders

### 1. Miniflux — The Minimalist's Choice

**What it is:** [Miniflux](https://miniflux.app/) is a self-hosted RSS reader written in Go, designed around a single philosophy: *do one thing, do it fast, get out of the way.* It's the anti-bloat option.

**Why you'd pick it:** You want a reader that loads instantly, works beautifully with keyboard shortcuts, and doesn't try to be a social network. Miniflux is the closest thing to "just the feeds, nothing else" that exists in the self-hosted world.

**The killer feature:** **It's genuinely fast.** Miniflux is a single Go binary backed by Postgres, and it *feels* like it. Pages render in milliseconds, the UI is clean and text-focused, and there's no JavaScript framework weighing it down. If you've ever been annoyed by a sluggish reader, Miniflux is the cure.

**Other things it does well:**

- **Fever API support.** Miniflux implements the Fever API, which means it works with a huge ecosystem of third-party mobile apps (Reeder, Unread, NetNewsWire, and more). You get the fast backend *and* your favorite native app.
- **No JavaScript required.** The web UI works with JS disabled, which is a nice privacy/security signal and a sign of how lean it is.
- **Built-in scraper.** Miniflux can fetch the full article content from truncated feeds, so you can read in place without clicking through.
- **Single binary.** Deployment is trivial — one container, one Postgres, done.

**The catch:** Miniflux is *opinionated* about minimalism. There's no plugin system, no themes, no social features. If you want a reader you can heavily customize, Miniflux will feel restrictive. It's also the least "pretty" of the three — functional, not flashy.

**Docker Compose:**

```yaml
services:
  miniflux:
    image: miniflux/miniflux:latest
    container_name: miniflux
    depends_on:
      - miniflux-db
    environment:
      - DATABASE_URL=postgres://miniflux:secret@miniflux-db/miniflux?sslmode=disable
      - RUN_MIGRATIONS=1
      - CREATE_ADMIN=1
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=change-me
    ports:
      - "8080:8080"
    restart: unless-stopped

  miniflux-db:
    image: postgres:16
    container_name: miniflux-db
    environment:
      - POSTGRES_USER=miniflux
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=miniflux
    volumes:
      - ./miniflux-db:/var/lib/postgresql/data
    restart: unless-stopped
```

---

### 2. FreshRSS — The Self-Hosted Google Reader

**What it is:** [FreshRSS](https://freshrss.org/) is a PHP-based RSS aggregator that's explicitly designed to be the self-hosted successor to Google Reader. It's the most feature-complete of the three, and the closest to a "drop-in replacement" for the reader you lost in 2013.

**Why you'd pick it:** You want the full Google Reader experience — categories, tags, full-text search, sharing, keyboard shortcuts, mobile apps — but on your own server. FreshRSS is the most "complete" reader here, and it's the one most people should start with.

**The killer feature:** **Full-text search.** FreshRSS indexes the *content* of your articles, not just the titles, so you can search across everything you've ever read. This is the feature that turns a reader from a "check the latest" tool into a "search my personal knowledge base" tool. Miniflux and TTRSS both have search, but FreshRSS's is the most robust.

**Other things it does well:**

- **Google Reader API compatibility.** FreshRSS implements the Google Reader API, which means it works with a *massive* ecosystem of mobile apps — Reeder, Fiery Feeds, NetNewsWire, and dozens more. This is the single biggest reason to pick FreshRSS: the app ecosystem.
- **Extensions.** FreshRSS has a plugin system with a real ecosystem — filters, themes, integrations with Readability, Wallabag, and more.
- **Flexible storage.** It runs on SQLite (zero-config, great for a single user), MySQL, or Postgres. SQLite means you can back up your entire reader as a single file.
- **Web scraping.** Like Miniflux, FreshRSS can fetch full article content from truncated feeds.

**The catch:** FreshRSS is PHP, which means it's heavier than Miniflux and requires a bit more care with the web server setup (though the Docker image handles most of it). It's also the most "traditional" of the three — the UI is functional but not modern, and it can feel dated compared to Miniflux's clean minimalism.

**Docker Compose:**

```yaml
services:
  freshrss:
    image: freshrss/freshrss:latest
    container_name: freshrss
    environment:
      - TZ=America/New_York
      - CRON_MIN=*/30
    volumes:
      - ./freshrss/data:/var/www/FreshRSS/data
      - ./freshrss/extensions:/var/www/FreshRSS/extensions
    ports:
      - "8081:80"
    restart: unless-stopped
```

FreshRSS uses SQLite by default with this setup — no separate database container needed. That's a real advantage for a single-user homelab: your entire reader is a folder you can back up with `rsync`.

---

### 3. Tiny Tiny RSS — The Tinkerer's Playground

**What it is:** [Tiny Tiny RSS](https://tt-rss.org/) (TTRSS) is the oldest of the three, a PHP-based reader that's been around since 2005 and has accumulated a deep, opinionated plugin ecosystem over two decades.

**Why you'd pick it:** You like to tinker. TTRSS is the most customizable of the three, with a plugin system that lets you do everything from filtering articles with regex to integrating with external services. If you've ever thought "I wish my reader could do X," TTRSS probably has a plugin for it.

**The killer feature:** **The plugin ecosystem.** TTRSS has plugins for filtering, scoring, tagging, sharing to social media, integrating with Pocket/Instapaper, and much more. It's the reader for people who want to *build* their own reading workflow, not just consume one.

**Other things it does well:**

- **Powerful filtering.** TTRSS's filter system is the most sophisticated of the three — you can auto-tag, auto-star, auto-hide, and auto-forward articles based on complex rules.
- **Scoring.** TTRSS can score articles based on keywords and rules, so your most important feeds float to the top.
- **Long history.** It's been around forever, which means it's battle-tested and has answers for almost every edge case.

**The catch:** TTRSS is the most *fiddly* of the three. The setup is more involved (it really wants Postgres, and the Docker setup has more moving parts), the UI is the most dated, and the project has had its share of maintainer drama over the years. It's also the least "just works" — you'll spend more time configuring it than the other two. The mobile app situation is also weaker than FreshRSS's Google Reader API compatibility.

**Docker Compose:**

```yaml
services:
  tt-rss:
    image: cthulhoo/ttrss-fpm-pgsql-static:latest
    container_name: tt-rss
    depends_on:
      - tt-rss-db
    environment:
      - TTRSS_DB_HOST=tt-rss-db
      - TTRSS_DB_USER=ttrss
      - TTRSS_DB_PASSWORD=secret
      - TTRSS_DB_NAME=ttrss
      - TTRSS_SELF_URL_PATH=https://rss.example.com/
    volumes:
      - ./tt-rss:/var/www/html
    restart: unless-stopped

  tt-rss-db:
    image: postgres:16
    container_name: tt-rss-db
    environment:
      - POSTGRES_USER=ttrss
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=ttrss
    volumes:
      - ./tt-rss-db:/var/lib/postgresql/data
    restart: unless-stopped
```

---

## The Decision Matrix

Here's the honest "which one should I run" answer, based on how you actually read.

| Your situation | Pick | Why |
|----------------|------|-----|
| You want it fast, minimal, and out of the way | **Miniflux** | Single binary, no bloat, keyboard-first |
| You want the full Google Reader experience | **FreshRSS** | Most features, best app ecosystem |
| You love plugins and custom workflows | **Tiny Tiny RSS** | Deepest plugin/filter system |
| You want zero-config, single-file backup | **FreshRSS** (SQLite) | Your whole reader is one folder |
| You read mostly on your phone | **FreshRSS** or **Miniflux** | Both work with Reeder/NetNewsWire via API |

**My honest recommendation for most people:** Start with **FreshRSS**. It's the most complete, it has the best mobile app support (via the Google Reader API), and the SQLite default means you can back up your entire reading life as a single folder. It's the closest thing to "set it up once and forget it" that this category offers.

If you're a minimalist who lives in the terminal and wants the fastest possible reader, **Miniflux** is a joy — it's the one I personally keep coming back to for its speed and cleanliness. And if you're the kind of person who reads the plugin list before the feature list, **Tiny Tiny RSS** is your playground.

---

## The Mobile App Question

The single most common question about self-hosted RSS is: *"but what about my phone?"* The answer is better than you'd expect, because all three of these tools speak standard APIs that a huge ecosystem of native apps already understands.

- **FreshRSS** implements the **Google Reader API**, which means it works with Reeder (iOS/macOS), Fiery Feeds, NetNewsWire, and dozens of others. This is the strongest mobile story of the three.
- **Miniflux** implements the **Fever API**, which is supported by Reeder, Unread, and NetNewsWire. Slightly smaller ecosystem than Google Reader API, but still excellent.
- **Tiny Tiny RSS** has its own API and a dedicated (if aging) mobile app, plus some third-party clients. It's the weakest of the three on mobile.

The practical upshot: **you don't have to use the web UI on your phone.** Point Reeder (or your app of choice) at your self-hosted reader, and you get a native, offline-capable reading experience that syncs back to your server. This is the killer combination — a self-hosted backend you own, with a polished native frontend you enjoy using.

---

## Getting Your Feeds In (and Out)

The other half of "owning your feed" is the feeds themselves. Here's the practical workflow:

1. **Find feeds.** Most sites still publish RSS, even if they don't advertise it. Try appending `/feed`, `/rss`, or `/atom.xml` to a URL, or use a feed-discovery tool. (This is also where you'll discover that some sites have quietly *killed* their RSS — a topic for another post.)
2. **Import your existing subscriptions.** If you're coming from Feedly, Inoreader, or another reader, export an OPML file and import it into your self-hosted reader. All three tools support OPML import/export, which is the universal format for feed subscriptions.
3. **Export regularly.** Your OPML file is your "feed insurance." Export it periodically and back it up alongside your other data. If your server dies, your subscriptions survive.

The beauty of OPML is that it's a *portable* format. You're never locked in — you can move from Miniflux to FreshRSS to TTRSS and back in five minutes, because your subscriptions are just a file.

---

## The Bottom Line

Self-hosting your RSS reader is the quiet, unglamorous move that pays off every single day. It's not as flashy as self-hosting your media or your AI stack, but it's arguably more important: **it's the tool that decides what information reaches your brain.**

The algorithmic feed is a product. It's designed to keep you engaged, not to keep you informed. RSS is the antidote — a feed you subscribe to, control, and own. And in 2026, running your own reader is a one-container job.

Whether you pick Miniflux for its speed, FreshRSS for its completeness, or Tiny Tiny RSS for its plugins, the important thing is that you're no longer renting your attention. Your media is self-hosted. Your photos are self-hosted. Your passwords are self-hosted. It's time your *reading* was too.

## Related Posts

- [Self-Hosted eBook Library: Calibre-Web vs Kavita vs Komga](/blog/2026-08-25-self-hosted-ebook-library-calibre-web-kavita-komga/) — The reading side of the "own your media" puzzle
- [Self-Hosted Audiobookshelf: The Complete 2026 Guide](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/) — Same ownership philosophy, different medium
- [Self-Hosted Music Streaming: Navidrome Setup Guide](/blog/2026-05-16-self-hosted-music-navidrome-soulseek/) — Owning your listening, not just your reading
- [WireGuard + Pi-hole: The Self-Hosted Privacy Stack](/blog/2026-04-21-wireguard-pihole-privacy-stack/) — The network layer that makes self-hosting private
- [Self-Hosted Web Analytics in 2026](/blog/2026-08-10-self-hosted-web-analytics-2026/) — Owning your data, not just your feeds

## Resources & Links

- [Miniflux](https://miniflux.app/) — Fast, minimal, Go-based reader
- [FreshRSS](https://freshrss.org/) — The self-hosted Google Reader successor
- [Tiny Tiny RSS](https://tt-rss.org/) — The plugin-rich veteran
- [OPML specification](http://opml.org/) — The portable format for feed subscriptions
- [Reeder](https://reederapp.com/) — Excellent iOS/macOS client that works with all three

*This is part of my ongoing self-hosting series. If you found it useful, the [ebook library comparison](/blog/2026-08-25-self-hosted-ebook-library-calibre-web-kavita-komga/) and the [Audiobookshelf guide](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/) are the natural next reads.*
