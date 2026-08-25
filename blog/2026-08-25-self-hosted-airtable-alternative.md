---
layout: post.njk
title: "Self-Hosted Airtable Alternative: Baserow vs NocoDB vs Teable vs Grist"
date: 2026-08-25
description: "Airtable is the spreadsheet-database everyone loves until the bill arrives. If you already run Postgres, you're one container away from a self-hosted Airtable. Here's a hands-on comparison of Baserow, NocoDB, Teable, and Grist — the four best ways to put a spreadsheet UI on your own database."
tags: ["airtable", "baserow", "nocodb", "teable", "grist", "postgres", "self-hosted", "database", "spreadsheet", "homelab", "open-source", "no-code"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-airtable-alternative"
---

Airtable is the tool everyone loves to use and hates to pay for. The spreadsheet interface is genuinely great — it's the database that non-engineers can actually operate. But the pricing scales with your rows, your collaborators, and your patience, and before long you're paying a SaaS subscription for what is, at its core, a pretty UI on top of a database you could run yourself.

Here's the thing most people miss: **if you already run Postgres, you're one container away from a self-hosted Airtable.** The hard part — the actual database — is already solved. What Airtable sells you is the *spreadsheet layer* on top. And that layer is now a commodity, with four serious open-source contenders fighting for the crown.

I've spent the last few weeks running all four against the same Postgres instance, and this is what I found. If you've been following my [database management playbook](/blog/2026-06-20-database-management-playbook-homelab/), this is the missing piece — the UI that makes your Postgres data actually *usable* by humans, not just by queries.

## The "Put a UI on Your Postgres" Angle

Let me reframe the whole category, because it changes how you evaluate these tools.

Airtable isn't a database. It's a **spreadsheet UI bolted onto a database engine.** The database part is the boring, solved part — Postgres has been doing it for 30 years. The interesting part is the UI: the grid, the views, the filters, the forms, the API, the permissions. That's what you're actually paying Airtable for.

Once you see it that way, the self-hosted options stop looking like "Airtable clones" and start looking like what they actually are: **different opinions about what the spreadsheet layer should be.**

- **Baserow** thinks the spreadsheet layer should be a clean, fast, no-code database builder.
- **NocoDB** thinks it should be a spreadsheet that *is* your database — literally a UI on top of your existing tables.
- **Teable** thinks it should be a Postgres-native, API-first database with a spreadsheet face.
- **Grist** thinks it should be a spreadsheet with a *formula engine* — Python-powered, relational, and scary-smart.

Same category, four very different philosophies. The right choice depends on which philosophy matches how you actually work.

## TL;DR Summary Table

| Tool | Best For | Postgres-Native | Docker | License | Formula Engine |
|------|----------|-----------------|--------|---------|----------------|
| **Baserow** | Clean no-code database builder | ❌ (own schema) | ✅ | MIT (core) | Basic |
| **NocoDB** | Spreadsheet UI on existing DB | ✅ | ✅ | AGPL-3.0 | Basic |
| **Teable** | Postgres-native, API-first | ✅ | ✅ | AGPL-3.0 | Basic |
| **Grist** | Python-powered relational spreadsheets | ❌ (SQLite/own) | ✅ | Apache-2.0 | **Python** |

## Baserow — The Polished All-Rounder

Baserow is the closest thing to a drop-in Airtable replacement, and it's the one I'd recommend to most people starting out. It's the top evergreen self-hosted result in this category for a reason: it's fast, it's clean, and it *feels* like a product rather than a project.

**What it does well:**

- **The UI is genuinely good.** Baserow's grid is snappy, the views (grid, gallery, form, kanban, calendar) are polished, and the whole thing feels like a commercial product. This matters more than you'd think — a database UI you dread opening is a database you won't use.
- **No-code friendly.** You can build a full relational database — tables, links, lookups, rollups — without writing a line of SQL. Non-technical collaborators can actually use it.
- **MIT-licensed core.** The open-source core is permissively licensed, which matters if you're building something on top of it.
- **Solid API and webhooks.** Baserow has a clean REST API and webhook support, so it plays well with n8n, Zapier, and your own scripts.

**What it doesn't do well:**

- **It's not Postgres-native.** Baserow manages its own schema internally. You can connect it to Postgres as its *storage backend*, but it doesn't just "put a UI on your existing tables" the way NocoDB does. If your goal is to browse tables you already have, Baserow isn't that tool.
- **The premium features are gated.** Row coloring, advanced permissions, and some view types live behind the paid tier. The core is MIT, but the *good* stuff is a subscription.
- **Formula support is basic.** Compared to Grist, Baserow's formula engine is a toy. Fine for simple lookups, not for real computation.

**Verdict:** Baserow is the best *starting point* — the most Airtable-like experience with the least friction. If you want a self-hosted Airtable and don't have strong opinions yet, start here.

## NocoDB — The Spreadsheet That *Is* Your Database

NocoDB takes the opposite approach from Baserow. Instead of building its own database, it connects to a database you already have — Postgres, MySQL, SQLite, SQL Server, and more — and renders it as a spreadsheet. The tagline is literally "turns any database into a smart spreadsheet."

**What it does well:**

- **True "UI on your Postgres."** This is the tool that most literally matches the "put a UI on your Postgres" angle. Point it at your existing database, and every table becomes an editable spreadsheet. No migration, no import, no schema changes.
- **Reads your existing schema.** If you already have a Postgres database with real tables, NocoDB just... shows them. This is huge if you're trying to give non-technical people access to data that already lives in Postgres.
- **Rich view types.** Grid, gallery, form, kanban — the standard Airtable spread, all available.
- **API generation.** NocoDB auto-generates REST and GraphQL APIs for your tables, which is genuinely useful.

**What it doesn't do well:**

- **AGPL-3.0 license.** This is the big one. AGPL is fine for internal use, but if you're building a commercial product on top of NocoDB, the copyleft terms can bite you. Worth reading the license carefully.
- **The UI is rougher.** NocoDB works, but it doesn't have Baserow's polish. It feels more like a powerful open-source project than a finished product.
- **Performance on large tables.** Rendering a 100k-row table as a spreadsheet is a known pain point. It's fine for most homelab use, but don't expect Airtable-level smoothness on huge datasets.

**Verdict:** NocoDB is the right choice if you *already have* a database and want to put a friendly face on it. It's the most literal "Airtable for your existing Postgres" — just be aware of the AGPL license if you're building something commercial.

## Teable — The Postgres-Native Newcomer

Teable is the newest of the four and the most interesting from a technical standpoint. It's built *on* Postgres from the ground up — not as a storage backend, but as the actual engine. Every Teable table is a real Postgres table, and it leans hard into being API-first.

**What it does well:**

- **Postgres-native by design.** This is the key differentiator. Teable doesn't abstract Postgres away — it *is* Postgres with a spreadsheet UI. If you're a Postgres person (and if you're reading this, you probably are), this is philosophically the most satisfying option.
- **API-first architecture.** Teable treats the API as a first-class citizen, not an afterthought. If you're building apps that need to read and write data programmatically, Teable's API is clean and fast.
- **Real-time collaboration.** Multiple users editing the same table in real time, which is a genuinely hard problem that Teable handles well.
- **Modern stack.** It's fast, it's actively developed, and it's clearly built by people who understand databases.

**What it doesn't do well:**

- **Younger ecosystem.** Teable is newer, which means fewer integrations, fewer community plugins, and less battle-testing than Baserow or NocoDB. The docs are thinner, and you'll be more on your own when things go wrong.
- **AGPL-3.0 license.** Same copyleft caveat as NocoDB.
- **Smaller feature surface.** Some of the polish — advanced view types, deep formula support — isn't there yet. It's catching up fast, but it's not as feature-complete as Baserow.

**Verdict:** Teable is the one to watch, and the one to pick if you're a Postgres-first developer who wants a spreadsheet UI that treats your database with respect. It's the most "engineer-friendly" of the four.

## Grist — The Spreadsheet With a Brain

Grist is the odd one out, and it's the one I find most fascinating. It's not really an Airtable clone at all — it's a *relational spreadsheet* with a full Python formula engine. Think "Excel, but every cell can be a Python expression, and tables can reference each other."

**What it does well:**

- **Python formulas everywhere.** This is Grist's killer feature. Every column can be computed with Python, which means you can do real data processing — not just `CONCAT` and `IF` — directly in the spreadsheet. For anyone who knows Python, this is a superpower.
- **True relational model.** Grist handles linked tables, lookups, and rollups natively and elegantly. It's genuinely a *relational* spreadsheet, not a flat grid with some link fields bolted on.
- **Apache-2.0 license.** The most permissive license of the four. No copyleft concerns at all.
- **Self-contained and robust.** Grist stores data in SQLite by default, which makes it dead simple to back up and move around. It's a single file, essentially.

**What it doesn't do well:**

- **Not Postgres-native.** Grist uses SQLite (or its own storage), not Postgres. If your whole point is "put a UI on my Postgres," Grist is the wrong tool — it's a *different* database, not a UI on yours.
- **Steeper learning curve.** The Python formula engine is powerful but not no-code. Non-technical users will find Grist intimidating compared to Baserow's point-and-click builder.
- **Different mental model.** Grist isn't trying to be Airtable. If you come in expecting Airtable, you'll be confused. If you come in expecting "a spreadsheet that can actually compute things," you'll be delighted.

**Verdict:** Grist is the best choice if you want *computation*, not just *storage*. It's the spreadsheet for people who find normal spreadsheets too dumb. Just don't expect it to be a Postgres UI — it's its own thing.

## How to Choose: A Decision Guide

Here's the short version, based on what you actually need:

**Pick Baserow if:**
- You want the closest thing to a drop-in Airtable replacement
- You need non-technical collaborators to be able to use it
- You want a polished, product-quality experience
- You don't need it to read your existing Postgres schema

**Pick NocoDB if:**
- You already have a Postgres (or MySQL) database with real tables
- You want to "put a UI on" data that already exists
- You're okay with AGPL licensing
- You don't mind a slightly rougher UI

**Pick Teable if:**
- You're a Postgres-first developer
- You want an API-first architecture
- You care about real-time collaboration
- You're willing to accept a younger, less battle-tested tool

**Pick Grist if:**
- You know Python and want real computation in your spreadsheet
- You need a true relational model
- You want the most permissive license (Apache-2.0)
- You don't need Postgres specifically

## The Docker Compose Quick Start

All four run in Docker, and getting them up is genuinely a five-minute job. Here's a minimal compose file to get you started with the two Postgres-native options (NocoDB and Teable) plus Baserow, all pointed at the same Postgres instance:

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: change-me
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped

  baserow:
    image: baserow/baserow:latest
    ports:
      - "8080:80"
    environment:
      BASEROW_PUBLIC_URL: http://localhost:8080
    volumes:
      - baserow_data:/baserow/data
    restart: unless-stopped

  nocodb:
    image: nocodb/nocodb:latest
    ports:
      - "8081:8080"
    environment:
      NC_DB: "pg://app:change-me@postgres:5432?d=app"
    depends_on:
      - postgres
    restart: unless-stopped

  teable:
    image: ghcr.io/teableio/teable:latest
    ports:
      - "8082:3000"
    environment:
      DATABASE_URL: "postgresql://app:change-me@postgres:5432/app"
    depends_on:
      - postgres
    restart: unless-stopped

  grist:
    image: gristlabs/grist:latest
    ports:
      - "8083:8484"
    environment:
      GRIST_SANDBOX_FLAVOR: gvisor
    volumes:
      - grist_data:/persist
    restart: unless-stopped

volumes:
  pgdata:
  baserow_data:
  grist_data:
```

A few notes from actually running these:

- **Baserow** bundles its own Postgres by default, so the `postgres` service above is optional for it — but if you want Baserow to use your existing Postgres, you can point it there via environment variables.
- **NocoDB** and **Teable** genuinely *use* the Postgres you give them. That's the whole point — they're UIs on your database, not databases of their own.
- **Grist** ignores Postgres entirely and uses its own storage. The `gvisor` sandbox flavor is recommended for security, since Grist executes Python formulas.

## The Bottom Line

The self-hosted Airtable category has matured to the point where there's no good reason to keep paying Airtable's per-seat, per-row pricing — *if* you're willing to run a container and accept a slightly rougher edge here and there.

The real insight is the reframe: **you already have the database.** Postgres is the hard part, and it's solved. What these four tools give you is the *spreadsheet layer* — the part that makes your data usable by humans instead of just by queries. And that layer is now free, open-source, and genuinely good.

My recommendation, compressed to a card:

1. **Starting fresh, want Airtable feel?** → Baserow.
2. **Already have Postgres tables?** → NocoDB (or Teable if you're API-first).
3. **Know Python, want real computation?** → Grist.
4. **Building a commercial product?** → Baserow (MIT) or Grist (Apache-2.0), avoid the AGPL tools.

Whichever you pick, you're trading a monthly SaaS bill for a Docker container and a bit of your own time. For most homelabbers — and honestly, for most small teams — that's a trade worth making.

---

*Have you ditched Airtable for a self-hosted alternative? Which one did you land on, and what made you pick it? I'd love to hear — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my [database management playbook](/blog/2026-06-20-database-management-playbook-homelab/), the [n8n alternatives review](/blog/2026-04-26-n8n-alternatives-review/), and the [self-hosted office suites comparison](/blog/2026-08-14-self-hosted-office-suites-bento-onlyoffice-collabora/).*
