---
layout: post.njk
title: "Self-Hosted CRM in 2026: Twenty vs EspoCRM vs Krayin vs SuiteCRM"
date: 2026-11-21
description: "Stop paying HubSpot or Salesforce to hold your customer list. These four self-hosted CRMs run on your own hardware — here's the honest comparison: Twenty (the AI-native Salesforce alternative), EspoCRM (the pragmatic workhorse), Krayin (the Laravel shop's pick), and SuiteCRM (the AGPL veteran). Plus which one actually fits a solo dev or freelancer's stack."
tags: ["self-hosted", "crm", "twenty", "espocrm", "krayin", "suitecrm", "salesforce", "hubspot", "homelab", "docker", "freelancer", "invoicing", "laravel"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-21-self-hosted-crm-twenty-espocrm-krayin-suitecrm"
affiliate: false
cta: true
---

# Self-Hosted CRM in 2026: Twenty vs EspoCRM vs Krayin vs SuiteCRM

Every "what should I self-host?" thread on r/selfhosted eventually hits the same wall: people want to kill their HubSpot or Salesforce subscription, but they don't know what to replace it with. That's a real pain point, because a CRM isn't a toy you spin up in Docker and forget about — it's where your *entire customer relationship* lives. Picking the wrong one means a painful migration later.

The good news: in 2026 there are four genuinely strong, actively-maintained open-source CRMs, and they split cleanly into four different use cases. This post is the honest comparison — what each one is, what it costs to run, what it's actually good at, and which one fits *your* stack. And because I've already written about [self-hosted invoicing](/blog/2026-09-12-self-hosted-invoicing-invoice-ninja-crater-akaunting) and [self-hosted cold email](/blog/2026-11-18-self-hosted-cold-email), the goal here is the full picture: **CRM + invoicing + email, all running on a single box, with no monthly SaaS bill.**

## The Four Contenders, At a Glance

| CRM | Stars (GitHub) | Language / Stack | License | Best For |
|-----|----------------|------------------|---------|----------|
| **Twenty** | ~61,000 | TypeScript (NestJS + Postgres + Redis) | AGPLv3 + enterprise carve-out | AI-native, modern, Salesforce-style pipeline |
| **Krayin** | ~24,000 | PHP (Laravel + Vue.js) | MIT | Laravel/PHP shops, permissive licensing |
| **SuiteCRM** | ~5,900 | PHP | AGPLv3 | SugarCRM lineage, maximum module depth |
| **EspoCRM** | ~3,600 | PHP | AGPLv3 | Pragmatic, lightweight, fast to stand up |

A note on the numbers before we go further: star count is a *popularity* signal, not a *fitness* signal. Twenty's 61k stars reflect that it's the hot new thing with an active VC-backed marketing engine. SuiteCRM's 5.9k reflect two decades of slow, steady maintenance rather than a dead project. Don't pick on stars alone.

---

## Twenty — The AI-Native Salesforce Alternative

[Twenty](https://github.com/twentyhq/twenty) is the reason this post exists. It bills itself, accurately, as "the open alternative to Salesforce, designed for AI," and it's the fastest-growing open-source CRM in the world right now. Created in late 2022, it's already crossed 60,000 stars and ships a genuinely polished, modern interface that makes most CRMs look like they're from 2012.

**What it is:** A full CRM built on NestJS (TypeScript), PostgreSQL, Redis, and BullMQ — a *modern* stack, not the PHP monoliths that define the rest of this list. It has objects, views, filters, a Kanban pipeline, and — the differentiator — first-class AI integration baked in, not bolted on.

**The honest catch — licensing.** Twenty is the one CRM on this list where you need to *actually read the license*. It's mostly AGPLv3, but with two qualifications baked into the LICENSE file:

1. Certain files marked `/* @license Enterprise */` are **not** AGPLv3 — they're under a commercial license.
2. The SDK/CLI/UI-component packages are MIT.

The practical takeaway: the open-source core is real and self-hostable for free, but some enterprise-tier features are gated behind the commercial license. For a solo dev or freelancer running it on their own box, that's almost never a problem. For a company reselling a hosted Twenty, it absolutely matters. AGPLv3 also means if you *modify* the code and offer it as a network service, you owe your changes back — a non-issue for personal use, a real consideration if you ever productize it.

**Self-hosting:** Docker Compose is the supported path ([docs.twenty.com](https://docs.twenty.com/developers/self-host/capabilities/docker-compose)), pulling Postgres and Redis alongside the app. It's heavier than the PHP CRMs — you're running a Node service, a queue worker, Postgres, and Redis — but that's the trade for the modern architecture.

**Best for:** Solo devs, freelancers, and small teams who want the most modern tool and don't mind a slightly heavier stack — and who specifically want AI-assisted CRM features rather than just a contacts database.

---

## EspoCRM — The Pragmatic Workhorse

[EspoCRM](https://github.com/espocrm/espocrm) is the one I'd tell most people to start with, and I want to be direct about why: it's the fastest to stand up, the lightest to run, and it's been quietly maintained since 2014 without ever chasing the hype cycle.

**What it is:** A PHP CRM that runs on a standard LAMP/LEMP stack (PHP 8.3–8.5), with a clean UI and a genuinely useful entity manager that lets you define your own fields, relationships, and layouts without touching code. It's AGPLv3 — free to use, modify, and self-host; the copyleft only bites if you resell a hosted version.

**Why it wins on pragmatism:**

- **Lightweight.** A single PHP app + MySQL/MariaDB. It'll run happily in a 1 GB LXC container, which matters if you're consolidating onto the same box as your invoicing and email.
- **Fast to stand up.** No separate queue worker, no Redis requirement for basic use, no Node build step. Install, point it at a database, go.
- **Extensible without a developer.** The entity/relationship editor means you can model "client → project → invoice" relationships yourself, which is exactly what a freelancer needs and what the heavier CRMs bury behind code.

**The trade-off:** It's not AI-native. It's a classic, well-built CRM — which is a feature if you want boring reliability and a drawback if you were hoping for the Twenty-style "AI summaries of every deal."

**Best for:** Freelancers and small businesses who want something that *just works*, runs light, and doesn't require babysitting. If you're the kind of person who read my [invoicing](/blog/2026-09-12-self-hosted-invoicing-invoice-ninja-crater-akaunting) and [cold email](/blog/2026-11-18-self-hosted-cold-email) posts and wanted the least-friction option, EspoCRM is almost certainly your answer.

---

## Krayin — The Laravel Shop's Pick

[Krayin](https://github.com/krayin/laravel-crm) is the sleeper on this list. It has ~24,000 stars — more than EspoCRM and SuiteCRM *combined* — but flies under the radar because it's a Laravel project in a PHP niche, and the Laravel community doesn't overlap much with the self-hosting community.

**What it is:** A free, open-source CRM built on Laravel (PHP) and Vue.js, targeting "SMEs and enterprises for complete customer lifecycle management." It's **MIT-licensed**, which is the single most important fact about it for a certain kind of reader: **there is no copyleft at all.** You can fork it, modify it, rebrand it, and even sell a hosted version without owing anything back. For anyone who's ever been bitten by AGPLv3's network-service clause, that's a genuine differentiator, not a footnote.

**Requirements:** PHP 8.2+, MySQL 8.0.32+ (or MariaDB). There's an official Docker install path too.

**The trade-off:** It's built by the Webkul team (the same folks behind Bagisto e-commerce), so its design instincts lean toward *e-commerce and multi-vendor* workflows. If you're a Laravel developer who wants a CRM you can bend to your will in a framework you already know, Krayin is compelling. If you're not a PHP developer and just want a CRM that works, EspoCRM's no-code entity editor is the friendlier route.

**Best for:** Laravel/PHP developers who want a permissively-licensed codebase they can extend in a framework they already know — or anyone for whom "MIT license" is a hard requirement.

---

## SuiteCRM — The AGPL Veteran

[SuiteCRM](https://github.com/SuiteCRM/SuiteCRM) is the elder statesman: it forked from SugarCRM Community Edition in 2013, and it's been the canonical "free alternative to Sugar/Salesforce" ever since. ~5,900 stars, AGPLv3, actively maintained (last push November 2026).

**What it is:** A sprawling, module-rich PHP CRM descended from SugarCRM. It has *everything* — accounts, contacts, leads, opportunities, cases, campaigns, workflow, reporting, email templates, and a marketplace of third-party plugins. If a feature exists in any CRM, SuiteCRM probably has a version of it.

**The honest trade-off:** "Sprawling" cuts both ways. SuiteCRM has the deepest feature set and the most enterprise-grade pedigree, but it's also the heaviest and most dated-feeling of the four. The UI is functional rather than modern, the codebase is a decade+ of accumulated PHP, and "lightweight" is not a word anyone uses about it. You run SuiteCRM when you *need* its depth and its SugarCRM compatibility, not when you want a quick win.

**Best for:** Organizations migrating off SugarCRM (drop-in-ish continuity), or anyone who needs maximum module depth and a mature plugin ecosystem — and accepts the heavier footprint in exchange.

---

## How I'd Choose (The Actual Decision Tree)

Here's the honest shortcut, because "it depends" is a cop-out:

1. **Want AI-native, modern, and don't mind a heavier Docker stack?** → **Twenty.**
2. **Want the fastest, lightest, most no-code option for a solo/freelance setup?** → **EspoCRM.**
3. **Are a Laravel/PHP dev who wants MIT-licensed code you can extend and even resell?** → **Krayin.**
4. **Migrating off SugarCRM, or need the deepest module set and don't care about a dated UI?** → **SuiteCRM.**

For *most* readers of this site — self-hosters and freelancers building a client stack on a single box — **EspoCRM is the default answer**, with Twenty as the upgrade path if you specifically want the AI features and have the resources to run it.

## The "Client Stack" Play — Why This Connects to Your Other Posts

The real insight isn't "pick a CRM." It's that a CRM is the *middle* piece of a three-part self-hosted client stack, and I've already covered the other two:

- **Invoicing:** [Invoice Ninja vs Crater vs Akaunting](/blog/2026-09-12-self-hosted-invoicing-invoice-ninja-crater-akaunting) — get paid.
- **Cold email:** [Self-hosted cold email](/blog/2026-11-18-self-hosted-cold-email) — reach new clients without torching your domain's sender reputation.
- **CRM (this post):** track who you reached and who you invoiced.

None of the four CRMs above do invoicing *well* — they all have some basic invoice/quote module, but a dedicated invoicing tool beats them on payment gateways, recurring billing, and tax handling. So the correct architecture for a solo dev isn't "one tool to rule them all," it's **CRM + invoicing + email, three lightweight services, one box.** EspoCRM (light PHP) + Invoice Ninja (light PHP) + a cold-email relay will all coexist comfortably in a single modest LXC or a Docker Compose file.

The moment you can stand that up, you've replaced roughly $100–300/month of HubSpot + Apollo + QuickBooks-style SaaS with a few containers on hardware you already own — and your customer data never leaves your box.

## The Limits (So This Doesn't Read Like "Free Salesforce")

I want to be honest about what self-hosted CRM is *not*:

- **You own the ops.** Backups, upgrades, and uptime are on you. A hosted CRM never wakes you up at 2 AM; a self-hosted one might (I'd point you at Watchtower and a solid backup cron — but that's a separate post).
- **AGPLv3 is not "free forever, no strings."** Three of these four (Twenty core, EspoCRM, SuiteCRM) are AGPLv3. That's fine for self-hosting; it only restricts you if you start *offering* the modified software as a service. Krayin's MIT is the exception.
- **AI features are uneven.** Twenty is genuinely AI-native. The others are classic CRMs where "AI" means a third-party integration you wire up yourself.
- **No hand-holding migration.** Moving off HubSpot/Salesforce into any of these is a data-export-and-remap job, not a button. Budget an afternoon.

None of this is a reason not to self-host. It's just the difference between a realistic plan and a fantasy.

## Next Steps

- **Want to try the lightest option first?** Spin up EspoCRM in Docker or an LXC, point it at a MySQL instance, and model one real client relationship end-to-end. Ten minutes to "it works."
- **Want the modern option?** Follow Twenty's [Docker Compose guide](https://docs.twenty.com/developers/self-host/capabilities/docker-compose) — accept the heavier footprint, enjoy the AI features.
- **Building the full client stack?** Pair your pick with the [invoicing](/blog/2026-09-12-self-hosted-invoicing-invoice-ninja-crater-akaunting) and [cold email](/blog/2026-11-18-self-hosted-cold-email) pieces, and you've killed three SaaS line items at once.

The trend here is the same one running through the rest of this site: your customer data is too valuable to rent, and too sensitive to hand to a vendor. Own it.
