---
layout: post.njk
title: "Can One Binary Replace Google Workspace? The Bento Experiment"
date: 2026-08-15
description: "Bento hit 3,989 stars in 30 days by shipping an entire office suite as a single HTML file. No Docker, no database, no server. I spent a week trying to run my actual work on it — and the answer to 'can one binary replace Google Workspace?' is more surprising than you'd think."
tags: ["self-hosted", "office-suite", "bento", "google-workspace", "single-binary", "homelab", "productivity", "privacy"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-15-bento-office-suite-self-hosted"
---

There's a specific kind of software that makes self-hosters sit up straight: the kind that deletes an entire category of infrastructure with a single file.

Bento is that kind of software. It launched on July 17, 2026, and thirty days later it has 3,989 stars, 267 forks, and a pitch that sounds like a dare: *"The office suite that fits in a file."*

One `.bento.html` file. About 560 KB. It contains the editor, the viewer, the presentation engine, the collaboration layer, the chart engine, the animation engine — and your actual slide content. Open it in any browser and you're editing slides. Save, and the file rewrites itself with your deck embedded inside.

No Docker. No PostgreSQL. No Redis. No RabbitMQ. No reverse proxy. No SSL certificates. No `docker-compose.yml` with four services and a JWT secret to rotate.

Just a file.

The question that follows is obvious, and it's the one I've been trying to answer for the last week: **Can you actually replace Google Workspace with one binary?**

## The Search Landscape Nobody's Fighting Over

Before I answer that, a quick detour into why this matters for anyone who writes about self-hosting.

Search for "self-hosted office suite" and you'll find a handful of comparison posts, most of them years old, most of them treating OnlyOffice and Collabora as the only two options that exist. Search for "replace Google Workspace self-hosted" and you'll find the same tired listicle format: OnlyOffice, Collabora, Nextcloud, maybe CryptPad if the author is feeling adventurous.

Nobody is writing about the *single-binary* angle. Nobody is asking whether the future of office software is a file that carries its own runtime. The search term is wide open — zero real competition — because the idea itself is only thirty days old.

That's the tell. When a category-defining idea ships and the search results haven't caught up yet, there's a window. Bento is sitting in that window right now.

## What "One Binary" Actually Buys You

The single-file architecture isn't a gimmick. It changes the economics of running office software in ways that matter more than feature checklists.

**Zero deployment.** There is no deployment. You download a file and open it. The "server" is the recipient's browser. When I say I "deployed" Bento to my homelab, what I actually did was `curl -O` a file and double-click it. That's the entire ops story.

**Zero maintenance.** No containers to update, no database to back up, no CVE to patch, no `docker compose pull` in a cron job. The file is the software, and the software is the file. When a new version ships, you download a new file. There's nothing running to break.

**Zero trust required.** Bento has an Offline mode that hard-blocks all network requests. The UI confirms it: "Offline mode — nothing leaves your machine." You can verify this in the source. Compare that to OnlyOffice, where collaboration routes through a server that can see your documents, or Google Workspace, where your documents live on someone else's disk by definition.

**Zero lock-in.** A `.bento.html` file opens in any browser, on any OS, forever — or at least as long as browsers can render HTML. There's no account, no subscription, no vendor that can shut down and take your files with it. The file *is* the software, so the software can't be discontinued out from under you.

**Zero barrier for recipients.** Send someone a Bento file and they need nothing. No install, no account, no internet. This is the part that actually changed my workflow: I stopped asking "what version of PowerPoint do you have?" and started just sending files.

## The Honest Limits of One Binary

Here's where I have to be straight with you, because the "one binary replaces everything" story has a catch.

**Bento is a presentation tool. That's it.** As of August 2026, Bento does slides and nothing else. No word processor. No spreadsheet. No PDF editor. The roadmap lists `bento/spaces` (notes), `bento/dash` (sheets), and `bento/vault` as future apps, but they don't exist yet. You cannot write a document in Bento. You cannot open a `.docx`. You cannot build a financial model.

**Mobile is view-only.** Phones can view and present decks, but editing is desktop-first. If you do last-minute slide tweaks from your phone, Bento will frustrate you.

**No template ecosystem yet.** The gallery at bento.page has starter templates, but it's nothing like decades of PowerPoint templates or Google Slides themes.

**Undo during live collaboration is snapshot-based.** The docs are honest about this: undoing during a collab session can revert a collaborator's concurrent edit to the same property. It's a known trade-off, not a bug, but it's real.

So the answer to "can one binary replace Google Workspace?" is: **no, not yet — but that's the wrong question.**

## The Right Question

The right question isn't "can one binary replace the whole suite." It's "how much of the suite do you actually use?"

Here's what I found when I audited my own Google Workspace usage over a month:

- **Presentations:** maybe 15% of my time. This is where Bento lives, and it's genuinely better than Google Slides for my use case — self-contained files, E2EE collaboration, AI-native editing.
- **Documents:** the bulk of my writing. Bento can't touch this. Neither can a single binary, because word processing is a different problem than slide layout.
- **Spreadsheets:** occasional, but when I need them I need real formulas and pivot tables. Bento's planned `bento/dash` won't replace Excel for me.
- **Email, calendar, drive:** the connective tissue. No single binary replaces these, and honestly, no self-hosted tool does it as seamlessly as Google does.

The insight isn't that Bento replaces Google Workspace. It's that **Google Workspace is a bundle, and most of us only need a fraction of the bundle.** Bento proves that the presentation fraction can be a single file. The question is whether the other fractions can follow.

## What Bento Gets Right That Google Doesn't

The single-file architecture isn't just a deployment trick. It enables things Google Workspace structurally can't do.

**Your files are actually yours.** A Bento file is a file. It sits on your disk. You can back it up, version it in git, sync it with Syncthing, encrypt it, put it on a USB stick. Google Docs lives in Google's cloud, and "export" is a feature they could theoretically change. Bento's data model is the file itself.

**AI can edit your deck without a cloud round-trip.** Because the document is plain JSON in a `<script>` block at the top of the file, any AI agent with filesystem access can edit it. Claude Code has a packaged `bento-slides` skill. You can point a local Ollama model at a deck and generate slides without anything leaving your machine. This is the first office tool I've seen that treats AI as a first-class user.

**E2EE collaboration with no server trust.** When you do collaborate, Bento uses AES-GCM with keys that live in the file itself. The optional sync relay stores ciphertext and learns nothing. Possession of the file is membership in the room. Google can't offer this because Google's business model requires the server to read your documents.

**The file is the app, so the app can't die.** This is the part that keeps me up at night in a good way. Google killed Google Reader, Google+, and a dozen other products. When a SaaS office suite shuts down, your documents become exports. When Bento "shuts down," nothing happens — the file you already have keeps working, because the software is inside it.

## The One-Binary Playbook

If you want to actually try replacing parts of Google Workspace with single-file tools, here's the playbook I've landed on after a week of testing.

**Step 1: Replace presentations with Bento.** This is the easy win. Download the file, rebuild your most-used slide templates, and start sending `.bento.html` files instead of Google Slides links. The self-contained format and E2EE collaboration are strictly better for anything you'd share externally.

**Step 2: Keep documents on OnlyOffice or Collabora.** For now, there's no single-binary word processor worth using. OnlyOffice wins on `.docx` compatibility; Collabora wins on resource efficiency and Nextcloud integration. Both are Docker stacks, not files — but they're the right tool for the job until someone ships a single-file word processor.

**Step 3: Watch the Bento roadmap.** `bento/spaces` (notes) and `bento/dash` (sheets) are the two apps that would turn Bento from "a brilliant presentation tool" into "a single-file office suite." If those ship and are half as good as the slides app, the calculus changes completely.

**Step 4: Don't try to replace email and calendar.** This is where the single-binary dream hits reality. Email and calendar are network services by nature — they require a server to receive and route messages. No single file replaces Gmail. Accept that and stop chasing it.

## The Bottom Line

Bento is not a Google Workspace replacement. It's something more interesting: **proof that the "office suite" doesn't have to be a monolith.**

For thirty years, office software has been a bundle — word processor plus spreadsheet plus presentation plus email plus calendar, all sold as one thing. Google Workspace is the apotheosis of that model. Microsoft 365 is the same model with a different logo.

Bento breaks the bundle. It says: *the presentation part of this can be a single file that carries its own runtime, encrypts its own collaboration, and never touches a server you don't control.* And it's right.

The question "can one binary replace Google Workspace?" has a boring answer today: no. But the more interesting question — "can the office suite be unbundled into single files?" — has an answer that's already shipping, and it's sitting at 3,989 stars and climbing.

The search results just haven't caught up yet.

---

*What's your take on the single-binary office suite? Are you using Bento, or are you waiting for the word processor and spreadsheet to ship? Find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my full [head-to-head comparison of Bento, OnlyOffice, and Collabora](/blog/2026-08-14-self-hosted-office-suites-bento-onlyoffice-collabora) and my guide to [self-hosted calendar tools](/blog/2026-06-26-self-hosted-calendar-tools-homelab).*
