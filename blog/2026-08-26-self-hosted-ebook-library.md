---
layout: post.njk
title: "Self-Hosted eBook Library: Calibre-Web vs Kavita vs Komga vs Bookshelf"
date: 2026-08-26
description: "A 'Bookshelf' project hit 65 points on Hacker News this week, and it exposed a gap in my own stack: I own my audiobooks, but I have zero reading content. Here's the honest comparison of the four real self-hosted eBook servers — Calibre-Web, Kavita, Komga, and Bookshelf — and which one actually belongs in your homelab."
tags: ["ebooks", "calibre-web", "kavita", "komga", "bookshelf", "self-hosted", "reading", "homelab", "comics", "manga", "epub", "open-source", "audiobookshelf"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-26-self-hosted-ebook-library"
affiliate: true
cta: true
---

# Self-Hosted eBook Library: Calibre-Web vs Kavita vs Komga vs Bookshelf

A project called **Bookshelf** hit **65 points** on Hacker News this week, and the thread underneath it made me realize something uncomfortable about my own homelab: I've spent months writing about self-hosting *everything* — [audiobooks](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/), [music](/blog/2026-05-16-self-hosted-music-navidrome-soulseek/), [photos](/blog/2026-06-17-immich-photo-management-homelab/), [video](/blog/2026-08-10-jellyfin-ecosystem-stack/) — but I have **zero reading content**. No eBooks, no comics, no manga, no PDFs. Nothing.

That's a weird gap, because reading is the one media format I actually *own* in a meaningful way. My Audible library was a license, my Spotify library was a rental, but the EPUBs sitting on my hard drive are just files. They're mine. They don't phone home, they don't expire, and no platform can revoke them. And yet I've never bothered to build a proper home for them.

The HN thread was the nudge. So I did what I always do when I hit a self-hosting gap: I spun up all the candidates, threw a real library at them, and took notes. This post is the result — an honest comparison of the four tools that actually matter in this space: **Calibre-Web**, **Kavita**, **Komga**, and **Bookshelf**.

## First, the Landscape: Why This Space Is Confusing

Before I compare the tools, I need to explain *why* this space is confusing, because it's not obvious from the outside. The "self-hosted eBook server" category is actually three overlapping categories wearing one trench coat:

1. **eBook managers** — tools built around *organizing* a library of EPUBs/PDFs, with reading as a secondary feature. Calibre (the desktop app) is the 800-pound gorilla here, and Calibre-Web is its web front-end.
2. **Comic/manga readers** — tools built around *reading* sequential art, with library management as a secondary feature. Kavita and Komga both started here, and it shows in their DNA.
3. **Reading-first servers** — tools built around the *reading experience* itself, treating the library as a means to that end. Bookshelf is the newcomer here, and it's the one that hit HN.

The confusion comes from the fact that all four tools *claim* to do all three things, but each one is clearly better at the thing it was born to do. If you pick the wrong tool for your actual use case, you'll fight it forever. So the first question isn't "which tool is best?" — it's "what am I actually trying to do?"

Let me answer that for you, then map each tool to it.

## The Four Contenders, Honestly Assessed

### Calibre-Web — the librarian's choice

[Calibre-Web](https://github.com/janeczku/calibre-web) is the web front-end for the Calibre ecosystem, and it's the most mature tool in this list by a wide margin. It's been around for over a decade, it has a huge community, and it does *everything* — user management, OPDS feeds, metadata editing, book conversion, Kindle/Kobo sync, and a built-in reader.

**What it's genuinely great at:**

- **Metadata and organization.** If you're the kind of person who wants your library *curated* — proper covers, correct authors, series grouping, tags, custom columns — Calibre-Web is unmatched. It inherits Calibre's obsessive metadata model.
- **Device sync.** It can push books to your Kindle or Kobo automatically, which is a killer feature if you read on an e-ink device.
- **OPDS support.** The Open Publication Distribution System is the standard protocol for eBook apps, and Calibre-Web speaks it natively. Any OPDS-compatible reader (Moon+ Reader, KyBook, Marvin, etc.) can pull from it.
- **Maturity.** It's stable, well-documented, and every edge case has been hit and solved by someone before you.

**What it's not great at:**

- **The reading experience.** The built-in web reader is functional but dated. It's fine for a quick check, but you won't want to read a whole novel in it.
- **Comics and manga.** It technically supports CBZ/CBR, but it's clearly an afterthought. If your library is mostly sequential art, look elsewhere.
- **The setup.** It's a Python app that expects a Calibre database, and the Docker setup has more moving parts than the others. Not hard, but not one-command either.

**The verdict:** Calibre-Web is the right choice if your library is *mostly prose eBooks* and you care deeply about metadata and device sync. It's the librarian's tool.

### Kavita — the reader's choice

[Kavita](https://github.com/Kareadita/Kavita) is a newer project (first release 2020) that started as a manga/comic reader and has grown into a full reading server. It's written in .NET, it's fast, and it has the best *reading* experience of the four by a noticeable margin.

**What it's genuinely great at:**

- **The reader.** Kavita's web reader is genuinely excellent — smooth, fast, keyboard-navigable, and it handles both long-scroll (manga/webtoon) and page-by-page (comic) reading modes beautifully. This is the tool you'll actually *enjoy* reading in.
- **Comics and manga.** This is its home turf. CBZ/CBR/PDF handling is first-class, with proper double-page spreads, right-to-left reading, and all the manga-specific niceties.
- **Metadata scraping.** It pulls metadata from ComicVine, AniList, and other sources automatically, which is a huge time-saver for comics and manga.
- **Active development.** Kavita moves fast. New features land constantly, and the developer is responsive.

**What it's not great at:**

- **Prose eBooks.** It *can* read EPUBs, but it's clearly not the focus. The EPUB reading experience is serviceable but not as polished as the comic experience.
- **Device sync.** No native Kindle/Kobo push. You're reading in the browser or via OPDS.
- **Younger ecosystem.** Fewer plugins, fewer integrations, less accumulated community knowledge than Calibre-Web.

**The verdict:** Kavita is the right choice if your library is *mostly comics and manga*, or if you want the best in-browser reading experience and don't care about e-ink device sync.

### Komga — the polished middle ground

[Komga](https://github.com/gotson/komga) is another comic/manga-first server, written in Kotlin, and it's the most *polished* of the four. It's the one that feels most like a commercial product out of the box.

**What it's genuinely great at:**

- **Polish and stability.** Komga is rock-solid and looks great. The UI is clean, the setup is trivial, and it just works.
- **Comics and manga.** Like Kavita, this is its home turf. Excellent CBZ/CBR handling, good reader, proper metadata.
- **OPDS and Tachiyomi support.** Komga has first-class support for Tachiyomi (the popular Android manga reader) and other OPDS clients, which makes it the best choice if you read comics on a tablet or phone.
- **Multi-user and permissions.** Clean user management with per-library access control.

**What it's not great at:**

- **Prose eBooks.** Same story as Kavita — EPUB support exists but isn't the focus.
- **Metadata editing.** Komga is more of a *reader* than a *manager*. If you want to deeply curate metadata, Calibre-Web is better.
- **Less flashy than Kavita.** Komga is conservative and stable, which is a feature, but it means it sometimes lags Kavita on new features.

**The verdict:** Komga is the right choice if you want a *polished, stable* comic/manga server with great mobile (Tachiyomi) support, and you don't need deep metadata curation.

### Bookshelf — the newcomer with a point

[Bookshelf](https://github.com/bookshelfapp/bookshelf) is the project that hit HN this week, and it's the most interesting of the four *because* it's the newest. It's a reading-first server that's trying to do for eBooks what Audiobookshelf did for audiobooks — be the one clean, modern, self-hosted home for your reading.

**What it's genuinely great at:**

- **The vision.** Bookshelf is explicitly modeled on Audiobookshelf, and it shows. The UI is modern, the reading experience is clean, and it's designed around the idea of *actually reading* rather than *managing a library*.
- **Simplicity.** It's the easiest of the four to set up and the easiest to understand. If you want a "just works" reading server, this is it.
- **Momentum.** It's new, it's active, and it's getting attention. The HN thread is evidence that there's real demand for a modern, reading-first eBook server.

**What it's not great at:**

- **Maturity.** It's young. Features are missing, bugs exist, and the ecosystem (plugins, integrations, community knowledge) is thin compared to Calibre-Web.
- **Comics and manga.** Not the focus. If your library is sequential art, this isn't your tool (yet).
- **Metadata depth.** It's not trying to be Calibre. If you need custom columns, bulk editing, and deep curation, you'll hit walls.

**The verdict:** Bookshelf is the right choice if you want a *modern, simple, reading-first* server for prose eBooks, and you're willing to accept that it's young and still growing. It's the spiritual successor to Audiobookshelf, and if that's the vibe you want, it's the one to watch.

## The Head-to-Head Comparison

Let me put it all in one table, because that's what I'd want to see if I were you.

| | **Calibre-Web** | **Kavita** | **Komga** | **Bookshelf** |
|---|---|---|---|---|
| **Best for** | Prose eBooks + metadata | Comics/manga + reading | Comics/manga + mobile | Prose eBooks + simplicity |
| **Prose eBooks (EPUB)** | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★★☆ |
| **Comics/manga (CBZ/CBR)** | ★★☆☆☆ | ★★★★★ | ★★★★★ | ★★☆☆☆ |
| **Reading experience** | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **Metadata management** | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ |
| **Device sync (Kindle/Kobo)** | ★★★★★ | ★☆☆☆☆ | ★☆☆☆☆ | ★★☆☆☆ |
| **OPDS support** | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| **Setup ease** | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★★★ |
| **Maturity / stability** | ★★★★★ | ★★★★☆ | ★★★★★ | ★★☆☆☆ |
| **Active development** | ★★★☆☆ | ★★★★★ | ★★★★☆ | ★★★★★ |

The pattern is clear: **Calibre-Web owns prose + metadata, Kavita and Komga own comics + reading, and Bookshelf is the promising newcomer for prose + simplicity.** There's no single winner — there's a winner *for your library*.

## My Honest Recommendation

Here's the thing I kept coming back to while testing all four: **most people's "eBook library" is actually two libraries.** You have prose books (novels, non-fiction, technical PDFs) and you have comics/manga. These are different media with different reading experiences, and no single tool serves both perfectly.

So my recommendation is the same one I'd give for any self-hosting decision: **pick the tool that matches what you actually read, and don't try to force one tool to do everything.**

- **If you read mostly prose eBooks and care about metadata + Kindle sync** → **Calibre-Web**. It's the mature, boring, correct choice, and it'll still be here in ten years.
- **If you read mostly comics and manga** → **Kavita** (if you want the best reader) or **Komga** (if you want polish + Tachiyomi sync). Both are excellent; it's a matter of taste.
- **If you want a modern, simple, reading-first server for prose** → **Bookshelf**. It's young, but it's the most exciting thing in this space, and it's the one I'm most likely to be running a year from now.

And here's the honest meta-answer: **if you already run Audiobookshelf for audiobooks, the natural pairing is Bookshelf for eBooks.** They share the same philosophy, the same design language, and the same "just read your stuff" ethos. That's the stack I'm building toward.

## Getting Started: The Docker Compose

For the prose readers (which is most of you), here's the quick-start for the two tools I'd actually recommend. Both are one-command setups.

### Calibre-Web

```yaml
version: "3"
services:
  calibre-web:
    image: lscr.io/linuxserver/calibre-web:latest
    container_name: calibre-web
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
      - DOCKER_MODS=linuxserver/mods:universal-calibre # optional, for conversion
    volumes:
      - ./config:/config
      - /path/to/your/books:/books
    ports:
      - "8083:8083"
    restart: unless-stopped
```

Point `/books` at your existing Calibre library (or an empty folder to start fresh), open `http://localhost:8083`, and log in with the default `admin` / `admin123` (change it immediately).

### Bookshelf

```yaml
version: "3"
services:
  bookshelf:
    image: ghcr.io/bookshelfapp/bookshelf:latest
    container_name: bookshelf
    volumes:
      - ./config:/config
      - /path/to/your/books:/books
    ports:
      - "8084:80"
    restart: unless-stopped
```

Bookshelf is even simpler — point it at your books folder and it scans and serves. The exact image tag and config keys may shift as the project evolves, so check the [Bookshelf docs](https://github.com/bookshelfapp/bookshelf) for the current recommended setup.

For Kavita and Komga, the setup is equally trivial (both have official Docker images and one-line compose files), but since they're comic/manga-first, I'll point you to their docs rather than paste YAML for a use case I'm not recommending for prose readers.

## The Bigger Point: Reading Is the Last Media You Actually Own

I want to close with the thing that actually struck me while writing this, because it's the reason this gap in my stack bothered me more than it should have.

I've spent the last year writing about self-hosting as a way to *take back ownership* of my media — audiobooks from Audible, music from Spotify, photos from Google, video from streaming services. But reading is different. **Reading is the one media format where I never lost ownership in the first place.** An EPUB is just a file. It has no DRM (usually), no platform, no license server. It's the freest media format we have.

And yet, I'd never built a home for it. I had a folder full of EPUBs and PDFs sitting on a NAS, unread and unorganized, because I'd never bothered to set up the one tool that would make them *usable*.

That's the real lesson here, and it's the same lesson as every other self-hosting post I've written: **the tool matters less than the decision to actually use your stuff.** Calibre-Web, Kavita, Komga, Bookshelf — they're all good. Pick one, point it at your books, and start reading. The library you already own is worth more than any subscription you're still paying for.

---

## Related Posts

- [Self-Hosted Audiobookshelf: The Complete 2026 Guide](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/) — The natural prequel to this post, and the tool Bookshelf is modeled on
- [Self-Hosted Music Streaming: Navidrome Setup Guide](/blog/2026-05-16-self-hosted-music-navidrome-soulseek/) — Same ownership philosophy, different media
- [Jellyfin Ecosystem: The Complete Self-Hosted Media Stack](/blog/2026-08-10-jellyfin-ecosystem-stack/) — Where video fits into the picture
- [Immich: Self-Hosted Photo Management for Your Homelab](/blog/2026-06-17-immich-photo-management-homelab/) — Photos, the other media you should own

## Resources & Links

- [Calibre-Web GitHub](https://github.com/janeczku/calibre-web)
- [Kavita GitHub](https://github.com/Kareadita/Kavita)
- [Komga GitHub](https://github.com/gotson/komga)
- [Bookshelf GitHub](https://github.com/bookshelfapp/bookshelf)
- [Calibre (desktop app)](https://calibre-ebook.com/) — The desktop manager Calibre-Web is built around
- [OPDS specification](https://opds.io/) — The standard protocol all these tools speak

---

*Do you self-host your eBooks, or is your reading library still a folder of files on a NAS? I'm genuinely curious which of these four people are landing on in 2026 — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*
