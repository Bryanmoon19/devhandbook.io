---
layout: post.njk
title: "The Entire Adobe Suite Is Being Rebuilt in Rust — What's Actually Usable in 2026"
date: 2026-10-10
description: "A Rust renaissance is quietly rebuilding Photoshop, Lightroom, Premiere, and Acrobat as open-source tools. I spent a month trying to cancel my Adobe subscription. Here's the honest verdict: what's usable, what to skip, and what's still not ready."
tags: ["adobe", "rust", "photoshop", "lightroom", "premiere", "de-subscription", "open-source", "self-hosted", "creative-tools", "photocraft", "compositor"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-10-adobe-suite-rebuilt-in-rust/"
affiliate: false
cta: true
---

Adobe has the most expensive subscription in my life. Not the biggest — my rent beats it — but the most *resented*. Every month, $54.99 comes out for Creative Cloud, and every month I use maybe 15% of what I'm paying for. I open Photoshop a few times, Lightroom once for a batch of RAW files, and Premiere sits untouched because I never got around to editing that video from last summer.

I've already done the de-subscription thing elsewhere on this site. I [quit Spotify](/blog/quit-spotify/), [replaced my office suite](/blog/self-hosted-office-suites/), and [dumped Docker](/blog/ditch-docker/). Adobe was the last holdout — the one tool I told myself I *needed*.

Then I found out something that changed my calculus: **a whole ecosystem of Rust projects is quietly rebuilding the entire Adobe suite**, and some of them are good enough to actually use. Not "good enough for nerds." Actually usable.

Here's what I found after a month of trying to cancel Adobe for real.

---

## Why Rust, Why Now

Before the tool roundup, a quick word on why this is happening *now*. Adobe has spent 30 years accumulating the most entrenched moat in software. Photoshop alone is millions of lines of C++ layered over decades of legacy code. Nobody "just rewrites Photoshop."

Unless you write it in Rust. Rust gives you C++-level performance with memory safety and a modern tooling ecosystem that makes *large* projects *manageable*. For graphics and media apps — where you're doing pixel-level manipulation, GPU-accelerated filters, and file-format parsing at high throughput — Rust is genuinely the right tool. And critically, a clean-room rewrite avoids the licensing and legal baggage of touching Adobe's code.

The result is a crop of projects with real momentum. Some have tens of thousands of GitHub stars. Some are already being used in production by actual creative professionals. Let me go through each one and give you my honest, first-person verdict.

---

## Storytold/Photocraft — The Photoshop Replacement

**GitHub:** [storytold/photocraft](https://github.com/storytold/photocraft) — **36,500+ stars**

This is the flagship. Photocraft is a clean-room reimplementation of Photoshop in Rust, and it's the most mature project in this entire list by a wide margin.

I loaded it up with a real photo and tried to do my actual workflow: open a layered PSD, clone-stamp out a distraction, apply a few adjustment layers, and export. Here's the honest report:

**What actually works:**
- **Layers, blend modes, masks.** The core compositing engine is real and correct. Layer groups, opacity, all the standard blend modes — they behave the way you expect.
- **Selection tools.** Lasso, magic wand, and the quick-select equivalent are genuinely usable. Not as smart as Photoshop's AI-driven subject select, but solid.
- **Adjustment layers.** Curves, levels, hue/saturation, and color balance all work on real 16-bit images.
- **PSD import.** This is the big one — it opens real Photoshop files with layers intact. Not perfectly (smart objects and some effects get flattened), but the basics survive.

**What's missing or rough:**
- **Content-Aware Fill** and Photoshop's newer AI features (generative fill) simply don't exist here. If your workflow leans on those, you'll feel it.
- **Filters** are sparse. You get the basics (blur, sharpen, distort), but the huge library of Photoshop's effects isn't there.
- **Performance** is good, not great. On my M4 Mac Mini it's snappy on 24MP images, but a 50-layer 100MP file makes it chug.

**Verdict: USABLE — for a specific kind of user.** If you're a photographer or designer doing layer-based compositing without heavy AI reliance, Photocraft can genuinely replace Photoshop for a lot of daily work. If you live in generative fill and smart objects, not yet.

---

## Storytold/Lightcraft — The Lightroom Replacement

**GitHub:** [storytold/lightcraft](https://github.com/storytold/lightcraft) — **7,900+ stars**

Lightroom is the one Adobe app I *actually* use weekly, so I was rooting for this one. Lightcraft is the Rust reimplementation of Lightroom's photo-management-and-editing workflow: catalog, non-destructive RAW processing, and export.

**What actually works:**
- **RAW processing.** It handles CR2, NEF, ARW, and DNG files using real demosaicing. The results are genuinely good — I compared side-by-side with Lightroom and couldn't tell the difference on most photos.
- **Non-destructive editing.** Exposure, white balance, highlights/shadows, tone curve, HSL, sharpening, noise reduction — all the core sliders are there and they work.
- **Library management.** It builds a catalog, rates, flags, and tags photos. Not as polished as Lightroom's, but functional.
- **Presets.** You can create, save, and apply presets, and there's import/export of `.xmp` sidecars.

**What's missing or rough:**
- **No cloud sync.** Lightroom's killer feature — edit on your laptop, see it on your phone — doesn't exist. You're fully local (which, given this site's de-subscription theme, is arguably a feature).
- **AI masking** (Lightroom's subject/sky/background select) isn't there. You're back to brushes and gradients.
- **The catalog can get sluggish** once you pass ~10,000 photos.

**Verdict: USABLE — arguably the best of the bunch.** For a pure local RAW workflow, Lightcraft is the most complete replacement in this list. If you don't need cloud sync or AI masking, this one genuinely lets you cancel Lightroom today.

---

## Storytold/Filmcraft — The Premiere Replacement

**GitHub:** [storytold/filmcraft](https://github.com/storytold/filmcraft) — **7,400+ stars**

Video editing is the hardest nut to crack, and it shows. Filmcraft is the Rust reimplementation of Premiere, and while it's the most ambitious project here, it's also the roughest.

**What actually works:**
- **Timeline editing.** Multi-track timelines, ripple/roll/slip edits, basic trimming — the fundamentals are there.
- **Transitions and basic effects.** Crossfades, wipes, color correction, audio leveling.
- **Export.** It renders to H.264/H.265 and a few other formats, and the export pipeline is decent.

**What's missing or rough:**
- **No multi-camera editing**, no motion graphics templates, no audio ducking — the pro features that make Premiere *Premiere*.
- **No GPU-accelerated rendering** in the way Premiere has it. Export on my M4 took noticeably longer than Premiere for the same footage.
- **Stability.** I hit crashes on longer timelines (20+ minutes) and on certain codec combinations. It's beta software in the truest sense.
- **Plugin ecosystem** is nonexistent. Premiere's third-party plugin world (Red Giant, Boris FX, etc.) is a big part of its value, and none of that carries over.

**Verdict: NOT READY — watch it, don't switch yet.** Filmcraft is an impressive technical achievement and it's improving fast, but for anything beyond simple cuts, Premiere (or DaVinci Resolve, which is free and excellent) still wins. Give it another year.

---

## Storytold/Pdfcraft — The Acrobat Replacement

**GitHub:** [storytold/pdfcraft](https://github.com/storytold/pdfcraft) — **6,700+ stars**

This one is interesting because I've already written about [ditching Adobe's PDF tools entirely](/blog/self-hosted-pdf-toolkit-2026/). Pdfcraft is the Rust take on Acrobat — a native PDF editor built on the same philosophy.

**What actually works:**
- **Text and image editing** inside existing PDFs — genuinely useful and better than most free online tools.
- **Form filling** and basic form creation.
- **Signing** with digital signatures.
- **Merge, split, rotate, reorder** — the basics you'd expect.

**What's missing or rough:**
- **No OCR.** If you have scanned documents, you're out of luck.
- **No Office format conversion** — it won't turn a Word doc into a PDF or vice versa.
- **Redaction** is basic, not the certified redaction that matters for legal/medical use.

**Verdict: USABLE — but you may not need it.** If you read my [PDF toolkit post](/blog/self-hosted-pdf-toolkit-2026/), you know I already solved this with a self-hosted stack. Pdfcraft is a nice native option if you want a desktop app instead of a server, and it's solid for basic editing. But Stirling PDF + bentopdf already covers most people.

---

## Robbietilton/Compositor — The Photoshop Alternative for Mac

**GitHub:** [robbietilton/Compositor](https://github.com/robbietilton/Compositor) — **15,000+ stars**

Compositor is different from the others: it's a native macOS app (Swift + Rust for the heavy lifting) that positions itself as a Photoshop alternative for the Mac crowd. It's more of a modern, opinionated image editor than a pixel-perfect Photoshop clone.

**What actually works:**
- **A genuinely beautiful, fast native app.** This is the best *feeling* tool in the list. It launches instantly, uses Metal, and feels like a first-class Mac citizen.
- **Non-destructive editing** with a modern, node-based approach.
- **Adjustment layers, masks, blend modes** — the core Photoshop concepts, but rethought with a cleaner UI.
- **Apple Pencil / tablet support** is excellent, better than Photocraft's.

**What's missing or rough:**
- **No PSD import** to speak of. If you have years of Photoshop files, this won't open them.
- **No text tool**, no shape tools — it's an *image* editor, not a full design tool.
- **Mac-only.** No Windows or Linux builds.

**Verdict: USABLE — if you're a Mac photographer, not a designer.** Compositor is a joy to use and perfect for photo retouching and compositing on a Mac. But it's not a drop-in Photoshop replacement — it's a cleaner, narrower tool that does image work exceptionally well. If you're a graphic designer doing layouts, text, and shapes, skip it.

---

## The Verdict Table

Here's the whole thing at a glance:

| Tool | Replaces | Stars | My Verdict |
|------|----------|-------|------------|
| **photocraft** | Photoshop | 36.5K | **USABLE** — great for layer-based work, no AI features |
| **lightcraft** | Lightroom | 7.9K | **USABLE** — best of the bunch, pure local RAW workflow |
| **filmcraft** | Premiere | 7.4K | **NOT READY** — impressive but unstable, use Resolve for now |
| **pdfcraft** | Acrobat | 6.7K | **USABLE** — but my self-hosted PDF stack already covers it |
| **Compositor** | Photoshop (Mac) | 15K | **USABLE** — gorgeous native Mac app, narrower scope |

---

## Can I Actually Cancel Adobe Now?

Here's the honest answer, after a month of trying.

**If you're a photographer:** Yes, mostly. Lightcraft handles your RAW workflow, Photocraft or Compositor handles your retouching, and my [self-hosted PDF stack](/blog/self-hosted-pdf-toolkit-2026/) handles documents. The one thing you'll genuinely miss is Adobe's AI masking and generative fill. If you can live without those, cancel.

**If you're a designer:** Sort of. Photocraft covers layer compositing, but if you live in Illustrator's vector world or InDesign's layout world, there's no Rust replacement for those yet. You'll keep Adobe (or use Affinity, which remains the best paid alternative).

**If you're a video editor:** No. Filmcraft isn't ready, and honestly it doesn't need to be — DaVinci Resolve's free tier is so good that Premiere's only real moat is ecosystem lock-in, not quality.

**My personal outcome:** I cut my Adobe subscription down from the full Creative Cloud ($54.99/month) to just Lightroom Classic ($9.99/month) while I finish migrating my photo library to Lightcraft. Net savings: $540/year. And the moment Lightcraft's catalog handles my library without hiccups, that last $9.99 goes too.

---

## The Bigger Picture

This isn't just a story about photo editors. It's the same de-subscription arc I've been writing about all year, now reaching the creative tools that seemed untouchable:

- I [quit Spotify](/blog/quit-spotify/) and built my own music setup.
- I [replaced my office suite](/blog/self-hosted-office-suites/) with open source.
- I [dumped Docker](/blog/ditch-docker/) for lighter alternatives.
- I [built a self-hosted PDF toolkit](/blog/self-hosted-pdf-toolkit-2026/) to ditch Acrobat.
- And now, the Rust renaissance is taking aim at Photoshop, Lightroom, and Premiere.

The pattern is the same every time: a tool starts as "technically impressive but not there yet," quietly crosses the "actually usable" line, and a year later the commercial alternative looks indefensible. These Rust projects are on that exact trajectory — photocraft and lightcraft have *already* crossed the line for a big chunk of users.

Adobe's moat is real, and it's not going to vanish overnight. But for the first time in my life, I can see the day when it does. And that day is a lot closer than Adobe wants you to think.

---

**Want to go deeper?** I wrote a full guide to the de-subscription toolkit across this site:
- [Ditch Adobe: Build Your Own Privacy-First PDF Toolkit](/blog/self-hosted-pdf-toolkit-2026/)
- [Self-Hosted Office Suites](/blog/self-hosted-office-suites/)
- [The De-Subscription Archive](/blog/)

*What creative tool are you trying to replace? Drop it in the comments — I'm keeping a running list of the best open-source alternatives and would love to add yours.*
