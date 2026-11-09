---
layout: post.njk
title: "Self-Hosted Resume Builder & Job Search Tracker: Keep Your PII Out of SaaS"
date: 2026-11-09
description: "Every 'ai resume builder' and 'resume builder' you've ever googled wants your name, address, work history, and phone number on its servers. Dossier (~4.9k★) flips the model: one profile, a tailored resume and cover letter for every job, and a full application tracker — all on your own hardware, with a local LLM if you want it."
tags: ["resume", "resume-builder", "cv", "job-search", "job-hunting", "ai-resume-builder", "dossier", "self-hosting", "privacy", "llm", "ollama", "docker", "homelab"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-resume-builder-job-search"
---

Here's a small experiment you can run in the next five minutes. Open a private browsing window and type "resume builder" into your search bar. Watch the autocomplete. Then type "ai resume builder." Watch it again.

What you'll see is a wall of *rich* results — every one of them a SaaS product that wants you to create an account, paste in your work history, and let their AI "optimize" your resume for the job market. Here's the thing none of them say out loud: **a resume is one of the most information-dense documents you own.** Your full name, address, phone number, email, ten years of employers, dates, titles, and salary-adjacent accomplishments — all in one place, attached to an account that links it to your identity.

Handing that to a resume SaaS is handing a company a near-complete PII dossier on you, in exchange for a PDF and a monthly subscription. And if you're job-hunting *while employed*, you've just told a third party — one whose other customers include recruiters and background-check firms — that you're looking.

The self-hosting answer to this is finally mature, and it's called [**Dossier**](https://github.com/AienTech/dossier) (~4.9k★, AGPL-3.0). It's a self-hosted job search and resume builder that keeps your entire career history on your own hardware and only sends data out when *you* decide it should.

---

## The Problem: "Free" Resume Tools Are the Product

The economics of the resume SaaS space are worth understanding, because they explain *why* the privacy angle matters more here than almost anywhere else in self-hosting.

A resume builder is a genuinely useful product. Turning a messy career history into a clean, ATS-friendly, well-designed PDF is real work. But the marginal cost of serving you that PDF is pennies. So the business model leans on everything *around* the PDF:

- **The account.** You sign up with an email that ties your resume to a persistent identity.
- **The upsell.** "AI tailoring," "cover letter generation," "ATS score," "job matching" — all premium tiers.
- **The data.** Your resume, your applications, your job-search behavior. Some resume platforms are *owned by or feed* recruiting and job-board ecosystems. Your "private" resume is the training data and the lead list.

Even the reputable ones that genuinely don't sell your data are still holding a copy of it, bound to an account, on a server you don't control, protected by a breach-disclosure policy you had no say in. The 2023-2026 wave of credential-stuffing and data-broker breaches should have taught us what happens to "we take your privacy seriously" when the database gets dumped.

Self-hosting doesn't just move the bytes to your basement. It removes the *business incentive* entirely, because there's no vendor whose revenue depends on what it can learn from your job search.

---

## Meet Dossier: Your Job Search, On Your Own Server

[Dossier](https://github.com/AienTech/dossier) is the project that anchors this space, and after reading its README and docs, it's clear why it's crossed 4.9k stars. The pitch is exactly the right one:

> Your job search, on your own server: one profile, a tailored resume and cover letter for every job, and every application tracked from draft to offer.

The mental model is **one master profile → many tailored documents → a full application pipeline.** You enter your career history once, and everything else derives from it. Let me break down what that actually means.

### The Profile (the single source of truth)

Instead of rewriting your resume from scratch every time, Dossier keeps one structured profile: basics, skills and languages, experience and volunteering, projects, education, certifications, publications, and references — in the order you choose. A "strength meter" counts what a complete profile needs, so you know what's missing. You can even start it by importing an existing PDF, Word, or Markdown resume.

This is the feature that quietly changes how you job-search. Because the profile is the source of truth, every resume and cover letter that comes out of it is *consistent* — no more "wait, did I say 'senior' at this job or that one?"

### The Base Resume (with themes)

Twelve built-in themes, a theme builder, live preview, and PDF rendering on the server. Duplicate a theme and tweak it, or share themes as files. This is the part that competes directly with the design-focused resume SaaSes — except the PDF is generated *locally* on your own box.

### Find Jobs (without joining a job board)

Dossier can search postings near your city (or anywhere) through JSearch (which aggregates LinkedIn, Indeed, and more), Adzuna, or FreeHire (company career pages). It also surfaces **startups that are hiring** from YC's job posts and Hacker News' monthly "Who is hiring?" thread, ranked against your profile. You save the good ones, dismiss the rest, and start an application from a posting with one click.

### Tailored Resumes & Cover Letters (the AI part)

Paste a job posting, and Dossier extracts the requirements, matches them against your profile, and drafts a tailored resume and cover letter in whatever tone you pick. The headline feature — and the one that separates it from every "AI resume" SaaS — is this:

> **Never invents experience:** drafts only use facts from your profile. What the posting asks for and your profile doesn't have is shown as a *gap*, not made up.

That's a genuinely important design decision. Most AI resume tools will happily hallucinate a credential you don't have, because a confident-looking resume converts to a paid plan. Dossier refuses to, because it's your tool, not a sales funnel. You refine the draft in a chat, regenerate any part (including every part of the cover letter — sender, date, recipient, greeting, sign-off, in the letter's language), undo changes, and keep private notes.

### Track Every Application

A board and table of every application, plus a dashboard with your funnel (last 30/90 days or all time), a week-by-week chart, and what's worth a look next. The entire pipeline from draft → applied → interview → offer, visible at a glance.

### Optional Integrations (all opt-in, all yours)

- **Gmail & Calendar:** connect your *own* Google OAuth client to send applications from your address with PDFs attached, read employers' replies, have the AI draft answers from your profile, and keep interviews in step with Google Calendar. Nothing is sent without your confirmation.
- **MCP connector:** use Dossier from Claude (desktop, mobile, or CLI) or another MCP app like n8n. It never sends or deletes anything.
- **Job agent:** save up to three named searches that run daily, score new postings against your profile, and keep the best — but it *never sends or applies*.

---

## The Privacy Model (What Actually Leaves Your Server)

Dossier's approach to privacy is the reason it belongs on a self-hosting blog, so let me be precise about it. The project maintains a [Privacy wiki page](https://github.com/AienTech/dossier/wiki/Privacy) and a `PRIVACY.md` that spells out exactly what stays and what goes.

The core promise: **your profile and documents stay on your own hardware by default.** You can point Dossier at a *local* model through Ollama or LM Studio, in which case the AI never talks to the internet at all — your resume content never leaves the machine for the purpose of generating documents.

If you choose a hosted model (any OpenAI-compatible API, Anthropic, or Mistral), then that provider receives "what it writes from" — the profile excerpts and posting text needed to generate a draft. That's the honest tradeoff, documented rather than hidden. Same with job search: the *search query* (your city, keywords) goes to the job source, but your profile does not. Gmail and Calendar integration is optional and uses your own OAuth client, not some vendor's.

This is the opposite of the resume SaaS default. There, the *data is the product*. Here, the data is yours, and every outbound call is a specific, documented, opt-in choice you made.

---

## Getting Started (About Five Minutes)

Dossier runs as a Docker container. All you need is Docker Desktop (macOS/Windows) or Docker Engine + Compose (Linux), and about 2 GB of free memory.

**1. Fetch the Compose file and generate secrets:**

```bash
mkdir ~/dossier && cd ~/dossier
curl -fsSL -o compose.yml https://raw.githubusercontent.com/AienTech/dossier/main/compose.production.yml
echo "POSTGRES_PASSWORD=$(openssl rand -hex 24)" > .env
echo "DOSSIER_SECRET=$(openssl rand -base64 32)" >> .env
```

**2. Choose your password** (Dossier stores only the hash, never the password):

```bash
docker run --rm -it ghcr.io/aientech/dossier hash-password
```

Add the output line to `.env` as `DOSSIER_PASSWORD=argon2id:…`.

**3. Start it:**

```bash
docker compose up -d
```

Open [http://localhost:3000](http://localhost:3000), sign in, and pick an AI model in **Settings → AI provider**. That's the whole thing.

**Prefer a single SQLite file to a PostgreSQL server?** Put `DATABASE_URL=file:/data/dossier.db` in `.env` and run the image on its own:

```bash
docker run -d --name dossier --env-file .env -v dossier-data:/data -p 127.0.0.1:3000:3000 ghcr.io/aientech/dossier
```

**Want to put it on a server** with a domain and HTTPS? The [installation guide](https://github.com/AienTech/dossier/wiki) covers Docker with Caddy, plain Node.js, CapRover, Coolify, and Dokploy. Give it at least 2 vCPUs and 2 GB of RAM.

There's also a **desktop app** for Windows and Linux from the [releases](https://github.com/AienTech/dossier/releases/latest) that runs everything locally with nothing else to install.

---

## The Honest Caveats

Dossier is a single-user tool, and it's open about what that means:

- **Desktop only.** Made for a laptop or desktop browser, not phones.
- **Single user.** One password, one profile, no multi-account support. It's for *you*, not a team.
- **English interface.** The app UI is English; documents can be written in ~21 other languages, with headings and dates localized.
- **One instance per database.** The nightly backups, AI job queue, and PDF renderer live inside the app's process, so you run one copy per database.
- **Resource floor.** PDF rendering uses Chromium (~520 MB peak), so give the container at least 768 MB — the README's sizing notes are refreshingly specific.

None of these are blockers for the intended use case — a single person managing their own job search on their own hardware. If anything, the "single user, one password, your data in your own PostgreSQL" framing is a *feature*, because it removes the entire class of account-management, multi-tenancy, and data-isolation bugs that plague the SaaS version.

---

## Why This Matters More Than Your Other Self-Hosted Apps

I run a lot of self-hosted stuff. Photo management, music, home automation, monitoring. For most of those, the privacy win is real but abstract — "my photos stay on my NAS" is a nice-to-have that mostly matters on principle.

A resume is different. It's not a nice-to-have. Your resume is:

1. **A complete identity document.** Name, address, phone, email, full employment history. That's enough to answer most security questions and seed a very convincing spear-phishing attack.
2. **A signal you're job-hunting.** Which, if your current employer (or a competitor, or a recruiter they work with) learns it, has direct career consequences.
3. **A standing asset.** You'll update it, reuse it, and reference it for the rest of your career. The account it lives in today is a liability that compounds over decades.

There's a reason the search terms are all rich autocomplete and the products are all "free to start." The demand is real, and the data is valuable. Self-hosting doesn't just remove the subscription — it removes the *counterparty*. Your job search becomes a thing that happens on your own machine, in your own database, with your own AI model if you want it, and the only data that leaves is the data you explicitly choose to send to a job board or a model provider.

That's the correct architecture for the most sensitive document you'll ever generate, and Dossier is the open-source project that finally does it well.

---

## The Bottom Line

Stop pasting your work history into a stranger's "free" resume builder. The self-hosted answer has arrived: **Dossier** gives you one master profile, tailored resumes and cover letters for every application, job discovery, and a full application tracker — all on your own hardware, with a local LLM if you want zero data leaving the building.

Install it in five minutes with Docker, point it at Ollama for fully-local document generation, and keep the single most PII-dense file you own where it belongs: on your own server, in your own PostgreSQL or SQLite database, behind your own password.

Your next job search can be private. The tool for it already has 4.9k stars and counting.

---

**Related posts:**
- [Self-Hosted LLM Gateway: LiteLLM vs OpenRouter](/blog/self-hosted-llm-gateway-lite-llm-vs-openrouter/)
- [Local LLMs on a Mac mini: A Practical Guide](/blog/local-llms-mac-mini-practical-guide/)
- [Vaultwarden: Self-Hosted Password Manager That Replaces LastPass & Bitwarden](/blog/vaultwarden-self-hosted-password-manager/)

---

*Links: [Dossier on GitHub](https://github.com/AienTech/dossier) · [Dossier docs](https://github.com/AienTech/dossier/wiki) · [Privacy](https://github.com/AienTech/dossier/wiki/Privacy) · [Dossier demo](https://dossier.aien.me)*
