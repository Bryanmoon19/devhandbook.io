---
layout: post.njk
title: "Self-Hosted Bookmark Manager Showdown: Linkwarden vs Hoarder vs Wallabag vs Karakeep (2026)"
date: 2026-08-28
description: "Your bookmarks are rotting. Every link you saved five years ago is a coin flip between 'still there' and '404'. A 2026 comparison of Linkwarden, Hoarder, Wallabag, and Karakeep — the four self-hosted tools that actually archive the page, not just the URL — with a decision matrix and copy-paste Docker Compose for each."
tags: ["bookmarks", "linkwarden", "hoarder", "wallabag", "karakeep", "link-rot", "self-hosted", "homelab", "read-it-later", "archiving", "docker", "pocket", "pinboard"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-28-self-hosted-bookmark-manager-showdown"
affiliate: false
cta: true
---

# Self-Hosted Bookmark Manager Showdown: Linkwarden vs Hoarder vs Wallabag vs Karakeep

Here's a small experiment. Go open your browser's bookmark bar — or your Pocket, your Pinboard, your Raindrop, whatever you've been dumping links into for the last decade — and click the first ten things you saved in 2020.

I'll wait.

If you're like most people, somewhere between three and six of those links are now dead. Not "moved." Not "paywalled." *Gone.* The domain lapsed, the blog was deleted, the company got acquired and the engineering blog was quietly taken down, the tweet was deleted, the GitHub repo was archived and then removed. The URL still sits in your bookmark manager like a tombstone, pointing at nothing.

This is **link rot**, and it's the quietest data-loss problem on the internet. Nobody's hard drive failed. No ransomware. The content just *evaporated*, and your bookmark manager — which you trusted to remember things for you — was only ever remembering a string of text, not the thing that string pointed to.

The fix is obvious once you see it: **stop saving links. Start saving pages.** A bookmark manager that only stores the URL is a bookmark manager that's already lost your data. A bookmark manager that fetches the page, snapshots the HTML, and archives a copy on *your* disk is a bookmark manager that survives the internet's entropy.

That's what this post is about. Four self-hosted tools that actually archive — Linkwarden, Hoarder, Wallabag, and Karakeep — compared honestly, with a decision matrix and copy-paste Docker Compose for each. And at the end, I'll point you at a companion tool I built to *measure* how much of your existing bookmark collection is already dead, so you know exactly how urgent this is.

## The Problem, Stated Precisely

Before we compare tools, let's be clear about what "archiving" actually means, because the four tools here do it in subtly different ways, and the difference matters.

When you save a bookmark, there are three levels of "saving" you could be doing:

1. **The URL only.** This is what your browser, Pocket, and most bookmark managers do. It's a pointer. When the target dies, the pointer points at nothing. This is not archiving; it's a to-do list of things to read before they vanish.

2. **The URL + a snapshot.** The tool fetches the page once, stores the HTML (and ideally the images, CSS, and a rendered screenshot), and keeps it on your disk. When the original dies, you still have the content. This is the minimum bar for "link-rot-proof."

3. **The URL + a snapshot + full-text search + offline reading.** The tool doesn't just store the page — it makes the archive *useful*. You can search inside everything you've ever saved, read it in a clean reader view, and export it in a format that isn't locked to the tool.

The four tools in this post all clear level 2. They differ on how well they do level 3, how heavy they are to run, and what their philosophy is. Let's meet them.

## The Four Contenders

### Linkwarden — The Archivist's Choice

**Linkwarden** is the most *deliberately* archiving-focused of the four. It was built from day one around the idea that a bookmark is a snapshot, not a pointer. When you save a link, Linkwarden fetches the page, stores a full HTML snapshot, captures a screenshot, and (optionally) saves a PDF. It can also archive to the Internet Archive's Wayback Machine as a belt-and-suspenders backup.

The killer feature is **preservation formats**. Linkwarden doesn't just keep the HTML — it can generate a PDF and a screenshot of every page you save, so even if the HTML rendering breaks in some future browser, you still have a pixel-perfect record. It also has a clean, modern UI, collections, tags, and a solid full-text search.

**Strengths:** Best-in-class archiving (HTML + screenshot + PDF + Wayback), polished UI, active development, good API.
**Weaknesses:** Heavier than the others (it's a full Next.js app with a Postgres database), and the "read it later" experience is more "archive manager" than "reading app."

### Hoarder — The AI-Assisted Hoarder

**Hoarder** is the new kid, and it's the one that's been getting the most attention in 2026. Its pitch is "bookmarks, but with AI." When you save a link, Hoarder fetches the page, extracts the content, and uses a local LLM to auto-generate tags, a summary, and a title. You can point it at Ollama and it'll do all of this on your own hardware, no cloud required.

The archiving story is solid — it stores the full content and a screenshot — but Hoarder's real differentiator is **automatic organization**. You dump a link in, and it comes back already tagged and summarized. For people with thousands of unsorted bookmarks, that's the difference between a tool you use and a tool you abandon.

**Strengths:** AI auto-tagging and summarization (local, via Ollama), clean UI, fast to set up, great mobile experience.
**Weaknesses:** The AI features are the point — if you don't want them, you're paying a complexity tax for nothing. Archiving is good but not as deep as Linkwarden's (no built-in PDF generation).

### Wallabag — The Read-It-Later Veteran

**Wallabag** is the oldest and most battle-tested of the four, and it's the one that most directly replaces Pocket or Instapaper. Its focus is **reading**, not archiving-as-such: it strips a page down to clean, readable text, stores it, and gives you a beautiful reader view, offline apps, and export to EPUB/MOBI/PDF.

Wallabag *does* archive — it stores the extracted content and can keep the original HTML — but its heart is in the reading experience. It's the tool you want if your primary use case is "save articles to read later, on my phone, offline, forever," rather than "build a permanent archive of everything I've ever found interesting."

**Strengths:** Mature, stable, huge ecosystem (apps for every platform, browser extensions, API), excellent reader view, EPUB export, RSS feeds of your saved articles.
**Weaknesses:** The archiving is content-extraction-first, so it's not a pixel-perfect snapshot of the original page. The UI is functional but dated compared to Linkwarden and Hoarder.

### Karakeep — The Hoarder Fork (Formerly Hoarder's Community Edition)

**Karakeep** is the plot twist. It's a fork of Hoarder that emerged when the Hoarder project's direction (and its AI-first focus) left some users wanting a leaner, more privacy-focused, more community-driven alternative. If Hoarder is "bookmarks + AI," Karakeep is "bookmarks, done well, without the AI if you don't want it."

Functionally, Karakeep keeps Hoarder's core — the clean UI, the content extraction, the screenshot archiving, the tagging — but strips back the AI dependency and leans into being a straightforward, self-hostable, no-cloud bookmark archive. It's the "just works" option for people who want Hoarder's polish without Hoarder's model requirements.

**Strengths:** Hoarder's UI and archiving without the AI complexity, active community fork, lighter resource footprint.
**Weaknesses:** Younger project, smaller ecosystem, and you're betting on a fork's longevity (though the community behind it is genuinely active).

## The Decision Matrix

Here's the honest summary. Pick based on what you actually care about:

| | **Linkwarden** | **Hoarder** | **Wallabag** | **Karakeep** |
|---|---|---|---|---|
| **Archiving depth** | ⭐⭐⭐⭐⭐ (HTML + screenshot + PDF + Wayback) | ⭐⭐⭐⭐ (content + screenshot) | ⭐⭐⭐ (extracted content + optional HTML) | ⭐⭐⭐⭐ (content + screenshot) |
| **Read-it-later experience** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **AI auto-organization** | ❌ | ✅ (local, via Ollama) | ❌ | ❌ (optional) |
| **Resource footprint** | Heavy (Next.js + Postgres) | Medium | Light | Medium |
| **Maturity / stability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Best for** | Serious archivists | AI-assisted hoarders | Readers | Hoarder fans who skip the AI |

**My recommendation, in one line each:**

- **Pick Linkwarden** if your goal is literally "build a link-rot-proof archive" and you want the deepest, most redundant snapshot possible.
- **Pick Hoarder** if you have a mountain of unsorted bookmarks and want AI to do the organizing for you.
- **Pick Wallabag** if you mostly want to *read* things later, offline, on your phone, and archiving is a nice-to-have.
- **Pick Karakeep** if you want Hoarder's polish but don't want to run a local LLM just to save a link.

## Docker Compose for Each

All four run in Docker. Here's the copy-paste setup for each, assuming you already have a Docker host (if you don't, my [Proxmox + Docker guide](/blog/2026-08-07-proxmox-nas-truenas-anas-turnkey/) is the place to start).

### Linkwarden

```yaml
# docker-compose.yml
services:
  linkwarden:
    image: ghcr.io/linkwarden/linkwarden:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/linkwarden
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - NEXTAUTH_URL=http://localhost:3000
    volumes:
      - ./data:/data/data
    depends_on:
      - postgres

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=linkwarden
    volumes:
      - ./pgdata:/var/lib/postgresql/data
```

Generate a `NEXTAUTH_SECRET` with `openssl rand -base64 32` and a `POSTGRES_PASSWORD` with `openssl rand -base64 24`, then `docker compose up -d`.

### Hoarder

```yaml
# docker-compose.yml
services:
  hoarder:
    image: ghcr.io/hoarder-app/hoarder:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - MEILI_MASTER_KEY=${MEILI_MASTER_KEY}
      - DATA_DIR=/data
      # Optional: point Hoarder at your local Ollama for AI tagging
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    volumes:
      - ./data:/data
    depends_on:
      - meilisearch

  meilisearch:
    image: getmeili/meilisearch:v1.6
    restart: unless-stopped
    environment:
      - MEILI_MASTER_KEY=${MEILI_MASTER_KEY}
    volumes:
      - ./meili:/meili_data
```

### Wallabag

```yaml
# docker-compose.yml
services:
  wallabag:
    image: wallabag/wallabag:latest
    restart: unless-stopped
    ports:
      - "8080:80"
    environment:
      - SYMFONY__ENV__DOMAIN_NAME=https://wallabag.example.com
      - SYMFONY__ENV__SERVER_NAME=Wallabag
    volumes:
      - ./data:/var/www/wallabag/data
      - ./images:/var/www/wallabag/web/assets/images
```

### Karakeep

```yaml
# docker-compose.yml
services:
  karakeep:
    image: ghcr.io/karakeep-app/karakeep:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - MEILI_MASTER_KEY=${MEILI_MASTER_KEY}
      - DATA_DIR=/data
    volumes:
      - ./data:/data
    depends_on:
      - meilisearch

  meilisearch:
    image: getmeili/meilisearch:v1.6
    restart: unless-stopped
    environment:
      - MEILI_MASTER_KEY=${MEILI_MASTER_KEY}
    volumes:
      - ./meili:/meili_data
```

## The Migration Problem (and Why You Should Care Now)

Here's the uncomfortable part nobody writes about: **migrating your existing bookmarks is the hard part.**

You've got years of links in Pocket, Pinboard, Raindrop, your browser, or a `bookmarks.html` file you exported in 2019. All four tools here can import from the common formats (Pocket and Pinboard exports, Netscape `bookmarks.html`, CSV), but the import only brings over the *URLs*. The archiving — the actual fetching and snapshotting — happens *after* import, when the tool crawls each URL.

And that's where the rot bites. If a link is already dead, the archive step can't save it. The content is gone. The import will dutifully add the URL, and the tool will dutifully record "404," and you'll have a beautifully organized list of tombstones.

This is why I built a **bookmark-rot-checker** — a small tool that takes your exported bookmarks and tells you, *before* you migrate, exactly how many are already dead, how many are redirecting, and how many are still alive. It's the triage step that tells you whether you're migrating a library or a graveyard. (I'll link it at the bottom.)

The takeaway: **the best time to start archiving was the day you saved your first bookmark. The second-best time is today.** Every day you wait, more of your saved links die.

## The Bottom Line

Your bookmarks are rotting, and the only fix is to stop treating them as pointers and start treating them as archives. All four of these tools will do that for you — the question is just which flavor of "archive" fits your life.

- **Linkwarden** is the archivist's choice: the deepest, most redundant snapshot, with PDF and Wayback backups.
- **Hoarder** is the AI-assisted choice: dump links in, let a local LLM tag and summarize them.
- **Wallabag** is the reader's choice: the best "read it later, offline, forever" experience, with EPUB export.
- **Karakeep** is the pragmatic choice: Hoarder's polish without the AI overhead.

Whichever you pick, the important thing is that you pick one and start archiving *now* — because the links you saved last year are already starting to die, and no bookmark manager can bring back a page that's already gone.

## Related Posts

- [Self-Hosted eBook Library: Calibre-Web vs Kavita vs Komga vs Bookshelf](/blog/2026-08-25-self-hosted-ebook-library-calibre-web-kavita-komga/) — Same "own your media" philosophy, applied to reading
- [Self-Hosted Audiobookshelf: The Complete 2026 Guide](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/) — The ownership argument that started this series
- [Proxmox + NAS: Turnkey TrueNAS/UNAS Setup](/blog/2026-08-07-proxmox-nas-truenas-anas-turnkey/) — Where to run these containers
- [Self-Hosted S3 at Home with MinIO](/blog/2026-08-23-s3-at-home-minio/) — Object storage for your archive's backups

## Resources & Links

- [Linkwarden GitHub](https://github.com/linkwarden/linkwarden)
- [Hoarder GitHub](https://github.com/hoarder-app/hoarder)
- [Wallabag GitHub](https://github.com/wallabag/wallabag)
- [Karakeep GitHub](https://github.com/karakeep-app/karakeep)
- [Internet Archive Wayback Machine](https://web.archive.org/) — The belt-and-suspenders backup Linkwarden can push to

*This is part of my ongoing self-hosting series. If you found it useful, the [eBook library guide](/blog/2026-08-25-self-hosted-ebook-library-calibre-web-kavita-komga/) and the [Audiobookshelf guide](/blog/2026-07-01-self-hosted-audiobookshelf-complete-guide/) are the natural next reads.*
