---
layout: post.njk
title: "The Rust Creative Suite Is Now Complete — Can You Actually Ditch Adobe *and* Microsoft Office?"
date: 2026-10-13
description: "Last week the clean-room Rust wave finished what it started: Word, Excel, and PowerPoint now have open-source replacements to match the Photoshop and Illustrator ones. That's the entire Adobe + Office stack rebuilt in Rust. Here's the honest, per-app verdict on what's daily-driver ready and what's still vaporware."
tags: ["rust", "adobe", "microsoft-office", "word", "excel", "powerpoint", "de-subscription", "open-source", "photocraft", "wordcraft", "gridcraft", "deckcraft", "creative-tools", "productivity"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-13-rust-creative-suite-complete-ditch-adobe-office/"
affiliate: false
cta: true
---

A week ago I wrote that [the Adobe suite was being rebuilt in Rust](/blog/2026-10-10-adobe-suite-rebuilt-in-rust/) — Photoshop, Lightroom, Premiere, and Acrobat, all getting clean-room open-source replacements with tens of thousands of GitHub stars. The obvious follow-up question was the one I couldn't answer then: *what about the other half of the subscription bill?*

Microsoft Office is the quiet titan of subscription fatigue. Most people don't resent it the way they resent Adobe's $54.99/month — because most people don't pay for it at all. They ride a work license, a student license, a family plan, or Google's free tier. But if you're self-employed, freelancing, or just trying to own your tools, Office 365 is $69.99/year for a single user and $99.99/year for a family. And unlike Adobe, you can't really live without *something* that opens a .docx.

I've been watching one GitHub org — [ArtCraft](https://github.com/storytold), the team behind the Rust suite — for a while. Three weeks ago they had the creative side: the image editors, the video editor, the PDF tool. Then, on **October 7th, 2026**, they shipped the other shoe: **WordCraft, GridCraft, and DeckCraft** — Word, Excel, and PowerPoint, rebuilt in pure Rust. All three in a single day.

That's the entire stack now. Adobe *and* Office. Here's the honest verdict on whether you can actually cancel both.

---

## The Whole Suite, One Place

First, the lay of the land. The ArtCraft org has shipped **fifteen** Rust applications, all clean-room reimplementations of commercial software, all open-source (MIT or Apache-2.0), all running natively on macOS, Windows, Linux, BSD — and in the browser via WebAssembly. Every single one is agent-drivable over MCP, which I'll come back to, because it's the part nobody else is talking about.

**The Adobe replacements** (I covered these in depth [last week](/blog/2026-10-10-adobe-suite-rebuilt-in-rust/)):

| App | Replaces | Stars (Oct 13) |
|---|---|---|
| PhotoCraft | Photoshop | ~54,500 |
| LightCraft | Lightroom | ~11,400 |
| FilmCraft | Premiere | ~11,700 |
| PdfCraft | Acrobat | ~11,700 |
| VectorCraft | Illustrator | ~8,000 |
| EffectCraft | After Effects | ~5,900 |
| DesignCraft | InDesign | ~3,500 |
| CADCraft | AutoCAD | ~3,500 |
| SoundCraft | Pro Tools | ~2,300 (pre-alpha) |

**The Office replacements** (the new half, all created October 7th):

| App | Replaces | Stars (Oct 13) |
|---|---|---|
| WordCraft | Microsoft Word | ~9,600 |
| GridCraft | Microsoft Excel | ~4,000 |
| DeckCraft | Microsoft PowerPoint | ~2,700 |

WordCraft alone went from zero to nearly 10,000 stars in **six days**. That's not a trickle of curiosity — that's a market saying "yes, please, I want to stop paying for Word."

---

## The Office Half: What Actually Works

I installed WordCraft, GridCraft, and DeckCraft on my Mac mini and pushed them through the workflows I'd actually use as a freelancer. Here's the straight report, because "it compiles" is not the same as "I'd trust it with a client deliverable."

### WordCraft — the strongest of the three

**GitHub:** [storytold/wordcraft](https://github.com/storytold/wordcraft) — **9,600+ stars, created Oct 7**

This is the one that's going to surprise people. WordCraft has the full Word workflow: the ribbon, styles, tables, track changes, references, and mail merge. It reads *and writes* real `.docx` files — which is the entire ballgame, because round-tripping a document with a client who's on actual Word is the make-or-break test.

**What works:**
- **The ribbon and styles.** It looks like Word, down to the live styles gallery. If you know Word, you already know WordCraft.
- **.docx round-trip.** Opens real Word files, saves real Word files. This is the thing every "Word alternative" gets wrong (looking at you, Google Docs with your mangled track changes).
- **Track changes and references.** The two features that actually matter for professional writing.

**The verdict:** this is the closest thing to a drop-in Word replacement I've seen outside of a Microsoft product. For a freelancer writing proposals, invoices, and reports, it's genuinely usable *today*. The browser/WebAssembly build means you can even run it without installing anything.

### GridCraft — solid bones, honest gaps

**GitHub:** [storytold/gridcraft](https://github.com/storytold/gridcraft) — **4,000+ stars, created Oct 7**

GridCraft is the Excel clone, and it's the one where I'm most honest about the gap. Spreadsheets are *hard* — people have built decade-long careers on Excel features most of us never touch.

**What works:**
- Tables with a totals row, conditional formatting, data bars, sparklines, and live charts.
- Formulas and the core grid workflow.

**What's missing:** the deep function library and the ecosystem. Excel has thousands of functions, Power Query, VBA, and thirty years of Stack Overflow answers. GridCraft has the fundamentals. For a simple budget, a schedule, or a data table, it's fine. For financial modeling with Power Query, it's not there yet.

**The verdict:** usable for the 80% use case, not yet for the 20% that defines Excel power users. Watch this one — it's moving fast, and the fundamentals are *correct*, which matters more than feature count.

### DeckCraft — early, but pointed the right way

**GitHub:** [storytold/deckcraft](https://github.com/storytold/deckcraft) — **2,700+ stars, created Oct 7, marked "early development"**

DeckCraft is the PowerPoint clone, and to their credit, the team labels it honestly as *early development*. It builds decks with themes, layouts, shapes, tables, charts, transitions, and animations, and opens/saves `.pptx`.

**The verdict:** the least mature of the three, and the team says so. If you present weekly to clients, keep your PowerPoint or Keynote for now. If you make a deck once a quarter, it's worth trying.

---

## The Part Nobody's Talking About: Every App Is Agent-Drivable

Here's the angle I think matters most to *this* audience, and it's the reason I wrote this post rather than just linking to the READMEs.

Every single one of these apps ships a **CLI and an MCP server**. That means an AI agent — Claude Code, Codex, OpenCode, whatever you run — can *drive* WordCraft, GridCraft, DeckCraft, PhotoCraft, the lot of them, headlessly.

Think about what that unlocks. Instead of "generate a Word doc by asking an LLM to emit XML and praying," you can have an agent open WordCraft, create a real document, set styles, insert a table, run mail merge, and save a `.docx` that a human client opens in actual Microsoft Word and sees zero difference. Same for a GridCraft spreadsheet with real formulas and charts, or a DeckCraft presentation with actual layouts and transitions.

That's a genuinely new capability. Google Docs and Microsoft 365 have clunky, partial APIs with rate limits and auth walls. These Rust tools expose their *entire* UI as agent commands. For anyone building agentic workflows around document generation — invoices, reports, proposals, slide decks — this is the missing piece that's been awkward to automate for years.

---

## So Can You Ditch Both Subscriptions?

The honest answer, with real numbers attached:

**Ditching Adobe:** mostly yes, with caveats. PhotoCraft, LightCraft, and PdfCraft are genuinely daily-driver for a lot of photographers and designers. The AI features (generative fill) aren't there, and if your workflow leans hard on them, you'll feel the loss. But for layer-based compositing, RAW processing, and PDF work, you can cut the cord. I covered the per-app verdicts [in the Adobe post](/blog/2026-10-10-adobe-suite-rebuilt-in-rust/).

**Ditching Office:** yes for Word, mostly for Excel, not yet for PowerPoint. WordCraft is the standout — it's the one I'd actually switch to. GridCraft is fine for simple spreadsheets. DeckCraft needs more time.

**The combined math:** Adobe Creative Cloud at $54.99/month is $659.88/year. Office 365 Family is $99.99/year. That's **~$760/year** for software that now has a viable, open-source, Rust alternative across *every* category. And these aren't the awkward open-source clones of ten years ago — they're fast, native, cross-platform, and — critically — agent-drivable.

I'm not going to tell you to cancel both tomorrow. I'm telling you the ceiling is gone. You can now genuinely live without either subscription, and the only real cost is the features you personally lean on.

---

## The Honest Skepticism

Two things keep me from full evangelist mode.

**First, this is still one org, moving fast.** The entire suite lives under a single GitHub organization (ArtCraft, at [storytold](https://github.com/storytold)). That's a double-edged sword: it means a coherent vision and shared libraries (real quality signal), but it also means the bus-factor is one. If that team burns out or gets acquired-and-stalled, the whole suite stalls together. Open source survives on community, and the community hasn't yet forked these into independent stewardship.

**Second, "clean-room reimplementation" is doing a lot of legal work.** These projects are careful to say they're clean-room, MIT/Apache-2.0, no Adobe or Microsoft code. But the *names* — WordCraft, GridCraft, DeckCraft — are walking right up to the trademark line, and a "reimplementation of Microsoft Word" is a phrase that invites a lawyer's attention. So far so good; just know this space could get legally spicy if the big two decide to flex.

Neither of those is a reason not to use them. They're reasons to watch the governance, not the code. The code is genuinely good.

---

## What I'd Actually Do (If I Were You)

1. **Try WordCraft first.** It's the highest-quality, lowest-risk swap. Install it, open a real `.docx`, and see if your workflow survives. Mine did.
2. **Keep one Office app for the edge cases.** For now, that's PowerPoint (DeckCraft is too early) and any Excel power features.
3. **Cut Adobe where it doesn't hurt.** If you're a photographer, PhotoCraft + LightCraft + PdfCraft cover the big three. Keep the Adobe sub only if you live in generative fill.
4. **Watch the agent angle.** This is the sleeper feature. If you're building any kind of document-generation automation, these tools' MCP servers are the cleanest path I've seen, and I'll write a dedicated post on driving WordCraft from an agent soon.

The de-subscription story I've been writing on this site — [quitting Spotify](/blog/quit-spotify-intentional-listening/), [replacing my office suite](/blog/self-hosted-office-suites-bento-onlyoffice-collabora/), [dumping Docker](/blog/ditch-docker-podman-vs-docker-homelab/) — just got its biggest chapter yet. For the first time, "cancel everything" isn't a fantasy. It's a download.

---

*All star counts and creation dates verified against the GitHub API on October 13, 2026. I'm not affiliated with ArtCraft; I'm just a guy who resents paying $760 a year for software that now has an open-source answer.*
