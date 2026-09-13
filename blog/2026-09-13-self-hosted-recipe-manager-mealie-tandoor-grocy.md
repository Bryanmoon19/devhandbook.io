---
layout: post.njk
title: "Self-Hosted Recipe Manager in 2026: Mealie vs Tandoor vs Grocy"
date: 2026-09-13
description: "Paprika now charges a subscription and your recipes are locked in a proprietary cloud. Here's the honest head-to-head of the three serious self-hosted recipe managers — Mealie, Tandoor, and Grocy — scored for import, meal planning, and mobile app quality, plus a working Docker Compose stack for the winner."
tags: ["mealie", "tandoor", "grocy", "self-hosted", "recipes", "cooking", "meal-planning", "homelab", "docker", "comparison"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-09-13-self-hosted-recipe-manager-mealie-tandoor-grocy/"
affiliate: true
cta: true
---

Your recipe collection is the one dataset that will outlive every app you've ever used. People keep recipes for decades — the chicken dish your grandmother taught you, the bread recipe you finally perfected, the weeknight pasta you make every Tuesday. And yet most people store them in an app that's one price hike, one acquisition, or one shutdown away from holding them hostage.

Paprika moved to a subscription. AnyList is monetizing your shopping habits. Big Oven shut down entirely and took thousands of home recipes with it. The self-hosted crowd has three serious answers, and they're all open source: **Mealie**, **Tandoor**, and **Grocy**.

The problem is that "self-hosted recipes" is deceptively hard. It's not enough to store a list — the *import* has to actually work when you paste a URL from a random food blog, the *meal planner* has to actually help you cook during the week, and the *mobile app* has to be usable with flour on your hands. Get any one of those wrong and you're back to screenshots in a camera roll.

I've run all three on my Proxmox homelab. Here's the honest breakdown, scored for the home cook who wants their recipes to outlive their apps.

## The One Question That Matters

Before the comparison, let's name the real pain point, because it's the thing every generic listicle skips:

> **Which one actually imports a recipe from any website, keeps it clean and searchable, and gives you a usable shopping list — without you retyping everything by hand?**

That's the whole game. A recipe manager where you have to hand-enter every ingredient is a chore you'll abandon in two weeks. And an import that chokes on half the food blogs on the internet is worse than no import at all. Everything below is scored against that question.

## The Three Contenders

**Mealie** — the modern all-rounder. Automatic recipe scraping from any URL, meal planning, shopping lists, and a genuinely clean UI. The "just works" choice for most home cooks.

**Tandoor** — the power user's pick. Deep recipe management, tagging, meal plans, shopping lists, and a more configurable (but steeper) setup. The people who outgrow Mealie's structure end up here.

**Grocy** — the full household ERP. Recipes are one module inside a much bigger system (inventory, chores, batteries, tasks). Overkill for recipes alone, but unbeatable if you want your pantry *and* your recipes in one place.

## The Scored Comparison

| | Mealie | Tandoor | Grocy |
|---|---|---|---|
| **URL import** | Excellent (scrapes most blogs) | Very good (recipe-scrapers) | Manual (no auto-scrape) |
| **Meal planning** | Good (week view, drag-drop) | Good (plans, multiple) | Basic (via "meal plan" module) |
| **Shopping list** | Good (auto from plan) | Good (auto from plan) | Excellent (inventory-aware) |
| **Inventory / pantry** | None | None | Excellent (first-class) |
| **Mobile app** | Good (PWA + native) | Good (PWA) | Fair (PWA, busy UI) |
| **Self-host difficulty** | Easy (one container) | Moderate (worker + DB) | Moderate (more config) |
| **Import from Paprika/AnyList** | CSV/JSON export import | CSV/JSON export import | None (manual) |
| **Learning curve** | Low | Medium | High |
| **Cost** | Free | Free | Free |

## The Winner: Mealie

For most people, **Mealie** is the answer. It's the closest thing to a drop-in replacement for Paprika — paste a recipe URL, it scrapes the ingredients, steps, and photo automatically, and drops a clean, searchable recipe into your collection. The meal planner is genuinely useful (drag recipes onto a week view, generate a shopping list from the plan), and the mobile experience is good — a PWA you can install to your home screen that feels native.

Here's a working Docker Compose stack:

```yaml
services:
  mealie:
    image: ghcr.io/mealie-recipes/mealie:latest
    restart: unless-stopped
    ports:
      - "9925:9925"
    environment:
      BASE_URL: https://mealie.yourdomain.com
    volumes:
      - ./mealie-data:/app/data
```

That's it — one container, one volume. On first launch, open `http://your-server:9925`, create your account, and you're ready to import. Paste a recipe URL and watch it get scraped in seconds.

### The gotchas (the part tutorials skip)

1. **The importer is good, but not magic.** Mealie uses a recipe scraper that works on most food blogs, but it will occasionally miss a step or mis-parse an ingredient from a messy layout. Always glance at the imported result before trusting it. The good news: the JSON-LD / schema.org markup most recipe sites use means the *majority* scrape cleanly.

2. **Set `BASE_URL` before you expose it.** Mealie generates links (and the mobile app talks to it) using `BASE_URL`. If you set it wrong — or leave it as localhost and then access from your phone — image and share links break. Set it to your real domain *before* first use.

3. **The mobile app needs HTTPS.** Like every self-hosted PWA, the phone clients will refuse plain HTTP in many cases. Put it behind a reverse proxy (Caddy, Nginx, Traefik) with a Let's Encrypt cert. This is non-negotiable if you want to check a recipe at the stove.

4. **Back up the `mealie-data` volume.** Your entire recipe collection, meal plans, and photos live in that one directory. A nightly `rsync` or a restic snapshot is your entire disaster-recovery plan. This is the dataset you said you'd keep for decades — don't leave its backup to chance.

## When to Pick Tandoor Instead

**Pick Tandoor** if you want *more* control than Mealie gives you — granular tagging, multiple meal plans (e.g. "regular week" vs. "guests coming"), a more powerful search, and a slightly more configurable setup. It's the choice for people who treat recipes as a serious personal database, not just a list.

The tradeoff is real: Tandoor runs as a web app with a background worker and needs a database (it ships with a bundled SQLite, but Postgres is recommended for larger collections). Its URL import is very good (it uses the same `recipe-scrapers` library family Mealie does), but the setup is a step more involved, and the UI is more utilitarian than Mealie's.

```yaml
services:
  tandoor:
    image: vabene1111/recipes:latest
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      SECRET_KEY: change-me-long-random-string
      DB_ENGINE: django.db.backends.sqlite
    volumes:
      - ./tandoor-static:/opt/recipes/staticfiles
      - ./tandoor-media:/opt/recipes/mediafiles
      - ./tandoor-db:/opt/recipes/database
```

## When to Pick Grocy Instead

**Pick Grocy** if you want your *entire household* in one system, not just recipes. Grocy is an ERP for your home — it tracks pantry inventory, expiry dates, chores, batteries, and tasks, with recipes and meal planning as one module. It's the choice for the person who wants "we're out of olive oil" to show up on the shopping list automatically because the inventory went to zero.

The tradeoff is steep: Grocy has no automatic recipe URL import (you enter recipes manually or via JSON import), the UI is dense and utilitarian, and the learning curve is the highest of the three. It's a power tool for people who love systems — not a Paprika replacement.

## What You Give Up vs. Paprika / AnyList

Let me be honest about the tradeoffs, because this is where self-hosting either sticks or fails:

- **You lose the "it just works" recipe browsing.** Paprika's built-in browser and one-tap save are genuinely good. Mealie's URL paste is close, but it's not a built-in mobile browser. Budget for occasionally cleaning up a scraped recipe.
- **You lose the polished native app.** Mealie's PWA is good, but it's not Paprika's native app. If you live in the mobile app, this is the biggest downgrade.
- **You gain ownership.** Your recipes, your server, your rules. No subscription, no data mining, no "we're sunsetting this feature" email that deletes your grandmother's bread recipe.
- **You gain a skill.** Running your own recipe server is the same muscle as running Immich or Jellyfin — and it compounds with everything else on this site.

## The Bottom Line

Self-hosted recipes are a solved problem in 2026 — you just have to accept that URL import is the one thing you'll occasionally babysit. Most people leaving Paprika or AnyList should start with **Mealie** (clean UI, great import, easy self-host, good mobile). If you want a serious recipe database with granular control, **Tandoor** is the power choice. If you want your pantry and recipes in one system, **Grocy** is the household ERP.

The point is the same one I keep making across this site: your recipes are the one dataset you'll still care about in twenty years. Don't leave them on someone else's server — and don't pay a subscription for the privilege — when running your own is this easy.

---

*Not ready to self-host yet? The pattern I recommend across this site applies here too: start with a spreadsheet before you stand up a server. And if you're building out the rest of your self-hosted stack, see [Vaultwarden for passwords](/blog/2026-04-19-vaultwarden-self-hosted-password-manager/), [self-hosted notes](/blog/2026-09-09-self-hosted-notes-joplin-notesnook-memos-standard-notes/), and [self-hosted budgeting](/blog/2026-09-11-self-hosted-budgeting-actual-budget-firefly-iii-ynab/).*
