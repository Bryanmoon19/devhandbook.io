---
layout: post.njk
title: "How I Use Claude Code to Contribute to an Open-Source Android/iOS App"
date: 2026-03-28
description: "A real walkthrough of contributing Prowlarr integration and Download Client support to ArrMatey — a KMP *arr client — using Claude Code as my daily coding partner. Includes the actual workflow, what works, and where it breaks."
tags: ["claude-code", "ai", "open-source", "kotlin", "kmp", "android", "ios"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/contributing-open-source-with-claude-code"
---

I'm not a full-time developer. I'm a personal banker by day. But in the last few months I've merged four pull requests into an open-source Kotlin Multiplatform app — Prowlarr search integration, a complete Download Client engine, and a handful of bug fixes that the maintainer actually liked enough to ship.

Claude Code is why that happened.

This isn't a pitch for the product. It's a walkthrough of the actual workflow I've built, what the experience is genuinely like, and where it falls apart — because most articles about AI coding tools are either pure hype or pure dismissal, and neither is useful.

## What ArrMatey Is and Why I Chose It

**ArrMatey is a free KMP client for the *arr ecosystem — Sonarr, Radarr, Prowlarr — and it's the right kind of project to cut your teeth on with an AI coding tool.**

The app is actively maintained by [Owen](https://github.com/owenlejeune), it has a clear architecture he's documented (UseCase pattern, ViewModel wrappers for iOS), and it covers both Android and iOS from a single shared codebase. That last part is what made it interesting — Kotlin Multiplatform means you write business logic once and then wire it up on both platforms separately. It's complicated enough that you actually need help, but small enough that you can understand the whole codebase.

I was already a user of the *arr stack — Sonarr for TV, Radarr for movies, Prowlarr as an indexer manager. ArrMatey didn't have Prowlarr integration yet. That felt like the right first feature to try.

## The Actual Workflow

**My Claude Code session starts with context, not code — drop in the architecture rules before asking for anything.**

Before every session, I paste Owen's architecture guidelines into the conversation. They're not long: UseCases return state objects, ViewModels only collect state and expose functions, one class per file, use `moko-strings` instead of hardcoded strings. This matters more than it sounds. Without this context, Claude writes reasonable Kotlin that doesn't fit the project conventions — and Owen will catch it in review. With it, the code usually matches the existing patterns on the first try.

Here's the rough shape of my sessions:

```
1. Open the project in VS Code
2. Start a Claude Code session
3. Drop in Owen's architecture rules
4. Show Claude 1-2 existing feature implementations as examples
5. Describe what I want to build
6. Review each file as it's written, ask questions
7. Build the app, fix what breaks
8. Run a code review pass before submitting PR
```

That last step is important. Before I submit anything to Owen, I do a full review pass with Claude and specifically ask: "What would a senior Kotlin developer flag here? What doesn't match the existing patterns?"

## The Prowlarr Feature: What Actually Happened

**Prowlarr integration touched 20+ files across Android and iOS — Claude held the architecture together so I could focus on the product decisions.**

The feature had three parts: indexer list (show all configured indexers and their status), search (query across all indexers at once), and grab (send a result directly to a download client). Each one follows the same layered pattern:

```
API Client → Repository Interface → Repository Implementation → UseCase → ViewModel → UI
```

In a purely manual workflow, this is six files per feature chunk, each with boilerplate that has to match the other layers. Claude handles all of that automatically once it sees the pattern. I describe the data model — what Prowlarr's API returns, what fields matter — and it generates the full stack in a pass.

What I actually spent my time on:

- **API shape discovery** — The Prowlarr API docs are good but not exhaustive. I'd test an endpoint, see what came back, and tell Claude "the response has these actual fields, not those." Quick iteration loop.
- **Platform-specific differences** — KMP shared code compiles to both platforms, but the UI layer is entirely separate. Android uses Jetpack Compose, iOS uses SwiftUI. Claude knows both, but iOS SwiftUI patterns in KMP (Swift ViewModel wrappers, `@ObservedObject` collection) are specific enough that I sometimes had to correct it.
- **Product decisions** — How do you show indexer status? What happens when a grab fails? Should the search results show seeds/leeches or not? These are judgment calls that I made and Claude implemented.

The first PR ([#44](https://github.com/owenlejeune/ArrMatey/pull/44)) came back with a code review from Owen. Real feedback, not canned stuff: use `BackButton` helper instead of inline back logic, use `Navigation<SettingsScreen>` wrapper, a few `else ->` missing from exhaustive `when` statements for future-proofing. I took that feedback, asked Claude to apply it, reviewed every change, and pushed the revision. Owen merged it.

That code review round-trip is the most valuable part of contributing to a real project. You get specific, architectural feedback from someone who knows the codebase better than you — and that feedback goes directly into your next session as context.

## Download Client Engine: The Harder Feature

**Four download clients (qBittorrent, Transmission, Deluge, SABnzbd), a full create/edit form, and inline validation — Claude drafted 90% of it correctly because I'd given it the Prowlarr code as an example.**

By the time I tackled download client management, I had a complete reference implementation from the Prowlarr work. The pattern was identical: state wrappers, UseCases, platform-specific ViewModels. Claude could look at the Prowlarr code and generate download client code that matched it structurally.

The one thing Claude got wrong on the first pass: validation. The form let you save a download client with an empty URL or label, which would cause a crash later when trying to connect. I caught it in testing. The fix was a validation pass before save, showing an inline red error state instead of silently submitting bad data. Simple, but I had to notice it was missing.

```kotlin
// What I added — Claude wrote it once I described what was needed
if (url.isBlank()) {
    _urlError.value = "URL is required"
    return
}
if (label.isBlank()) {
    _labelError.value = "Label is required"  
    return
}
```

This is the pattern: Claude generates the structure, I use the feature and notice what's wrong, we fix it together.

## Where Claude Code Actually Helps

**Claude is best at pattern work — the repetitive, architecture-mandated boilerplate that has to be right but doesn't require judgment.**

Some concrete things it's genuinely good at:

- **Boilerplate to pattern** — "Here's the Sonarr data model, write a Prowlarr equivalent." Works every time.
- **Cross-platform translation** — "Here's the Android Compose screen, write the iOS SwiftUI equivalent." Mostly works; needs review for KMP-specific idioms.
- **Code review mode** — "What would you change about this?" Catches things I miss — inconsistent naming, missing null checks, functions that could be extracted.
- **Error diagnosis** — Paste a compile error and the relevant code, it usually spots the issue immediately. KMP compilation errors can be gnarly (shared code that compiles fine for Android but fails for iOS).
- **Upstream merge conflicts** — The project moves fast. When there's a conflict between my feature branch and upstream changes, Claude can understand both sides and write the resolution. Saves a lot of context-switching.

## Where It Breaks Down

**The model doesn't know what it doesn't know about your specific codebase, so you have to tell it before it tells you the wrong thing.**

A few honest limitations:

**Hallucinated APIs.** Early on, before I knew the codebase well, Claude would sometimes reference helper functions or extensions that didn't exist in ArrMatey. It would generate code that looked correct but wouldn't compile because it was calling something from a generic Kotlin/Compose context that Owen's project didn't have. Now I paste in the relevant existing code before asking for new code — fixes this almost entirely.

**Platform-specific Swift KMP idioms.** The way KMP exposes shared Kotlin flows to Swift is non-standard. You need `@ObservedObject` ViewModel wrappers, specific collection patterns to avoid crashes on iOS. Claude knows SwiftUI, but it sometimes writes code that works fine in a pure SwiftUI project and fails in the KMP context. I've learned to recognize the warning signs.

**Knowing when to stop.** Claude will keep generating code until you tell it to stop. For complex features, it's tempting to ask for everything at once — full API client, repository, UseCase, ViewModel, Android screen, iOS view, all in one go. This usually produces something you have to rewrite large chunks of. Better to go layer by layer and verify each one before moving on.

## The Bigger Picture

I think the people dismissing AI coding tools are imagining the wrong use case. If you're a senior engineer who already knows the architecture and just needs to type less, maybe the value isn't there. But if you're trying to contribute to an existing codebase in a language you're still learning, on a platform (KMP) you're unfamiliar with, against architecture conventions you didn't design — the tool closes a massive gap.

Owen's code reviews don't go easier on me because I used AI. The feedback is the same as it would be for anyone. What's different is that I can actually submit something worth reviewing in the first place, iterate on feedback quickly, and build up a body of contributions that taught me how KMP projects are actually structured.

Four PRs in three months. None of them would have shipped without this workflow.

---

**The project:** [ArrMatey on GitHub](https://github.com/owenlejeune/ArrMatey)

**The PRs:** [Prowlarr integration (#44)](https://github.com/owenlejeune/ArrMatey/pull/44) · [Download Client Engine (#43)](https://github.com/owenlejeune/ArrMatey/pull/43)
