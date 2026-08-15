---
layout: post.njk
title: "Self-Hosted Office Suites: Bento vs OnlyOffice vs Collabora — Can You Replace Google Workspace?"
date: 2026-08-14
description: "Bento hit 3,989 stars in 30 days — the office suite that fits in a single HTML file. But can it actually replace Google Workspace? I put Bento, OnlyOffice, and Collabora head-to-head: real Docker configs, honest trade-offs, and the answer to whether one binary can replace your entire productivity stack."
tags: ["self-hosted", "office-suite", "bento", "onlyoffice", "collabora", "google-workspace", "homelab", "docker", "productivity"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-14-self-hosted-office-suites-bento-onlyoffice-collabora"
---

There's a new project tearing through GitHub right now, and it's doing something I haven't seen before: shipping an entire office suite as a single HTML file.

[Bento](https://github.com/nyblnet/bento) launched on July 17, 2026. Thirty days later, it has 3,991 stars, 267 forks, and a community that's already building templates, plugins, and AI integrations. The pitch is audacious: *"The office suite that fits in a file."* One `.bento.html` file carries its own viewer, editor, and presenter. Open it in any browser. Edit it. Present it. Send it. The recipient needs nothing — the file *is* the software.

It's the kind of idea that makes you stop and think: *Could I actually replace Google Workspace with this?*

The honest answer is more interesting than yes or no. Bento is brilliant at one thing. OnlyOffice and Collabora are brilliant at different things. And depending on what you actually need from an office suite, the right answer might be one, two, or all three of them — or none at all.

I spent the last week running all three in my homelab, pushing them through real workflows, and trying to answer the question: **Can you actually replace Google Workspace with self-hosted tools in 2026?**

Here's what I found.

## The Contenders at a Glance

| | Bento | OnlyOffice | Collabora |
|---|---|---|---|
| **GitHub Stars** | 3,991 ⭐ | 6,815 ⭐ | 3,318 ⭐ |
| **First Release** | July 2026 | July 2014 | October 2020 |
| **License** | MIT | AGPL-3.0 | MPL-2.0 |
| **Deployment** | Single HTML file (~560 KB) | Docker stack (PostgreSQL + Redis + RabbitMQ) | Docker stack (LibreOffice + WOPI) |
| **Documents** | ❌ (slides only) | ✅ .docx editor | ✅ .docx editor |
| **Spreadsheets** | ❌ (planned: bento/dash) | ✅ .xlsx editor | ✅ .xlsx editor |
| **Presentations** | ✅ (the whole product) | ✅ .pptx editor | ✅ .pptx editor |
| **PDF/Forms** | ❌ | ✅ | ❌ (viewer only) |
| **Real-time Collab** | ✅ E2EE, CRDT-based | ✅ (server-mediated) | ✅ (server-mediated) |
| **Mobile** | View + present only | View + basic editing | View + basic editing |
| **AI Integration** | ✅ First-class (JSON doc model) | ❌ (plugin ecosystem) | ❌ (plugin ecosystem) |
| **Offline** | ✅ Fully offline mode | ❌ (server required) | ❌ (server required) |
| **Resource Usage** | Zero (client-side) | 4-8 GB RAM recommended | 2-4 GB RAM recommended |

## Bento: The Office Suite That Fits in a File

Let's start with the newcomer, because it's genuinely doing something different.

### What Bento Is

Bento is a presentation tool — and right now, *only* a presentation tool. It's not a word processor. It's not a spreadsheet. The roadmap lists `bento/spaces` (notes), `bento/dash` (sheets & tables), and `bento/vault` as future apps, but as of August 2026, Bento is a PowerPoint replacement and nothing else.

But as a PowerPoint replacement, it's remarkable.

The entire application is a single HTML file — about 560 KB compressed. That file contains the editor, the viewer, the presentation engine, the collaboration layer, the chart engine, the animation engine, and your actual slide content. You download it, open it in a browser, and you're editing slides. Save, and the file rewrites itself with your deck embedded inside.

### What Makes Bento Different

**The file is the app.** This isn't a gimmick. When you send someone a `.bento.html` file, they don't need to install anything. They don't need an account. They don't need internet access. They open the file in any modern browser and they can view your presentation, edit it, and save their own copy. The software travels with the data.

**Local-first, provably.** Bento has an Offline mode toggle. Flip it on, and the app hard-blocks all network requests. No telemetry, no update checks, no collaboration pings. The UI confirms: "Offline mode — nothing leaves your machine." This isn't marketing; you can verify it in the source.

**E2EE collaboration.** When you do collaborate, Bento uses AES-GCM encryption with keys that live in the file itself — never on a server. The optional sync relay stores ciphertext and learns nothing. Possession of the file is membership in the room. Rotate the keys, and you've revoked access. The relay source is about one file. You can read it in five minutes.

**CRDT-based merging.** Bento uses its own Conflict-free Replicated Data Type for collaboration, with character-level text merging. Offline edits merge back precisely. The CRDT is fuzz-tested across hundreds of thousands of convergence checks. This is serious engineering for something that ships as a single HTML file.

**AI-native design.** Because the document is plain JSON in a `<script>` block at the top of the file, any AI agent with filesystem access can edit your deck. Claude Code users get a packaged `bento-slides` skill. Chatbots can round-trip the JSON. You can point Ollama at a deck and have a local model generate slides without anything leaving your machine. This is the first office tool I've seen that treats AI as a first-class user, not an afterthought.

**Morph transitions.** Elements that share an `id` animate between slides — position, size, color, gradients. Duplicate a slide, rearrange elements, and the motion designs itself. It's the kind of feature you'd expect in Keynote or PowerPoint, built into a 560 KB HTML file.

### What Bento Isn't

Bento is not a Google Workspace replacement. It's not even a Google Slides replacement — yet. Here's what's missing:

- **No word processor.** You can't write a document in Bento. You can't open a `.docx` file. The roadmap has `bento/spaces` for notes, but it doesn't exist yet.
- **No spreadsheet.** `bento/dash` is planned. Today, you can put a chart on a slide, but you can't build a financial model.
- **No PDF editing or forms.** OnlyOffice handles this. Bento exports to PDF but doesn't edit PDFs.
- **Mobile is view-only.** Phones can view and present decks, but editing is desktop-first. This is a real limitation if you do last-minute slide tweaks from your phone.
- **No template ecosystem (yet).** The gallery at bento.page has starter templates, but it's nothing like the decades of PowerPoint templates or Google Slides themes available.
- **Undo during collaboration is snapshot-based.** The docs are honest about this: undoing during live collab can revert a collaborator's concurrent edit to the same property. It's a known trade-off.

### How to "Deploy" Bento

This is the best part: there's nothing to deploy.

```bash
# Download the single file
curl -O https://bento.page/releases/slides/Bento_Slides.bento.html

# Open it
open Bento_Slides.bento.html
```

That's it. No Docker. No database. No reverse proxy. No SSL certificates. The file is the app.

If you want the optional sync relay for collaboration:

```bash
# Clone the repo
git clone https://github.com/nyblnet/bento.git
cd bento/server/sync-worker

# Deploy to Cloudflare Workers
npx wrangler deploy
```

The relay is stateless, stores only ciphertext, and the source is about one file. You can audit it in five minutes.

### Who Bento Is For

- **People who give presentations** and want them to work forever, on any computer, without installing anything
- **Privacy-conscious teams** who need E2EE collaboration without trusting a server
- **AI-heavy workflows** where you want agents to generate and edit slides programmatically
- **Conference speakers, teachers, consultants** who send decks to clients and don't want "what version of PowerPoint do you have?" conversations
- **Anyone tired of Google Slides** who doesn't need the rest of Google Workspace

### Who Bento Is Not For

- **People who need a word processor or spreadsheet** — Bento is slides-only in 2026
- **Mobile-first editors** — editing requires a desktop browser
- **Enterprise procurement teams** — there's no vendor to call, no SLA, no support contract
- **People who need 100% PowerPoint compatibility** — Bento is its own format; export to PDF, not `.pptx`

## OnlyOffice: The Full Suite That Actually Works

If Bento is the brilliant newcomer doing one thing exceptionally well, OnlyOffice is the veteran that does *everything* competently.

### What OnlyOffice Is

OnlyOffice Docs is a full online office suite: word processor, spreadsheet editor, presentation editor, and PDF form filler. It's been around since 2014, has 6,815 GitHub stars, and is used by organizations from universities to government agencies. It's the closest thing to Google Workspace you can self-host.

The key differentiator: **OnlyOffice uses Office Open XML as its native format.** `.docx`, `.xlsx`, `.pptx` — these aren't import/export targets. They're the actual file format. This means near-perfect compatibility with Microsoft Office documents. When someone sends you a `.docx` with tracked changes, complex tables, and embedded charts, OnlyOffice renders it correctly. Collabora (based on LibreOffice) is good at this too, but OnlyOffice's OOXML fidelity is generally considered best-in-class among open-source options.

### What OnlyOffice Gets Right

**Complete office suite.** Documents, spreadsheets, presentations, and PDF forms — all in one deployment. If you're replacing Google Workspace, this is the closest feature match.

**Excellent Microsoft compatibility.** I tested a dozen complex `.docx` files — legal documents with tracked changes, financial models with pivot tables, presentations with custom animations. OnlyOffice handled all of them. The OOXML rendering is genuinely production-grade.

**Real-time collaboration.** Multiple users can edit the same document simultaneously, with paragraph-level locking and version history. It works like Google Docs: you see other people's cursors, changes appear in real time, and comments thread properly.

**Plugin ecosystem.** Macros, spell-checking, translation, YouTube embedding, photo editing, speech recognition — there's a marketplace of plugins that extend the editors.

**Integrates with everything.** Nextcloud, ownCloud, Seafile, Alfresco, Confluence, Jira, Moodle, SharePoint — OnlyOffice has connectors for most platforms you might already be running. If you self-host Nextcloud, adding OnlyOffice gives you Google Docs-style editing inside your existing file manager.

**Desktop and mobile apps.** Free desktop editors for Windows, macOS, and Linux. Mobile apps for iOS and Android with basic editing capabilities.

### What OnlyOffice Gets Wrong

**It's heavy.** The Docker deployment needs four containers: Document Server, PostgreSQL, Redis, and RabbitMQ. Recommended specs are 4-8 GB RAM. On my Proxmox LXC with 4 GB allocated, it ran fine for 1-2 concurrent users but struggled with large spreadsheets.

**The AGPL license.** OnlyOffice Community Edition is AGPL-3.0, which means if you modify the source code and expose it over a network, you must release your modifications. This is fine for most homelab users but can be a concern for commercial deployments. The enterprise edition (with more features) requires a paid license.

**Mobile editing is limited.** The mobile apps can view documents and do basic text edits, but complex formatting, spreadsheet formulas, and presentation editing are desktop-only. This is the same limitation as Google Workspace's mobile apps, but it's worth knowing.

**No E2EE.** Collaboration goes through the server. The server can see your documents. If you're running it on your own hardware, this is probably fine — but it's not the "server learns nothing" model that Bento offers.

**The Docker setup is non-trivial.** Here's what a minimal deployment looks like:

```yaml
version: "3.8"

services:
  onlyoffice-document-server:
    image: onlyoffice/documentserver:latest
    container_name: onlyoffice-docs
    ports:
      - "8088:80"
      - "8443:443"
    environment:
      - JWT_ENABLED=true
      - JWT_SECRET=your-jwt-secret-here
      - JWT_HEADER=Authorization
      - DB_TYPE=postgres
      - DB_HOST=onlyoffice-db
      - DB_NAME=onlyoffice
      - DB_USER=onlyoffice
      - DB_PWD=your-db-password
      - RABBITMQ_SERVER_URL=amqp://onlyoffice:your-rabbit-password@onlyoffice-rabbitmq
      - REDIS_SERVER_HOST=onlyoffice-redis
    volumes:
      - ./logs:/var/log/onlyoffice
      - ./data:/var/www/onlyoffice/Data
      - ./fonts:/usr/share/fonts/truetype/custom
    depends_on:
      - onlyoffice-db
      - onlyoffice-rabbitmq
      - onlyoffice-redis
    restart: unless-stopped

  onlyoffice-db:
    image: postgres:14
    container_name: onlyoffice-db
    environment:
      - POSTGRES_DB=onlyoffice
      - POSTGRES_USER=onlyoffice
      - POSTGRES_PASSWORD=your-db-password
    volumes:
      - ./postgres:/var/lib/postgresql/data
    restart: unless-stopped

  onlyoffice-rabbitmq:
    image: rabbitmq:3-management
    container_name: onlyoffice-rabbitmq
    environment:
      - RABBITMQ_DEFAULT_USER=onlyoffice
      - RABBITMQ_DEFAULT_PASS=your-rabbit-password
    restart: unless-stopped

  onlyoffice-redis:
    image: redis:7-alpine
    container_name: onlyoffice-redis
    restart: unless-stopped
```

That's four containers, a JWT secret to manage, and a database to back up. It's not unreasonable — if you're already running a homelab with a dozen Docker services, this is par for the course. But it's a far cry from Bento's "download a file and open it."

### Who OnlyOffice Is For

- **Anyone replacing Google Workspace** who needs documents, spreadsheets, and presentations
- **Teams that exchange `.docx`/`.xlsx`/`.pptx` files** with Microsoft Office users
- **Nextcloud users** who want integrated document editing
- **Organizations that need an on-premises office suite** with real-time collaboration

## Collabora: The LibreOffice-Powered Alternative

Collabora Online is the web-based version of LibreOffice, developed by Collabora Productivity. It's the engine behind Nextcloud Office, ownCloud Online, and several other self-hosted productivity platforms.

### What Collabora Is

Collabora is a full office suite — word processor, spreadsheet, presentation — powered by LibreOffice's rendering engine. It uses the Open Document Format (ODF) natively but imports and exports Microsoft formats. It's been in development since 2020 (the online version; LibreOffice itself dates back decades) and has 3,318 GitHub stars.

### What Collabora Gets Right

**LibreOffice compatibility.** If a document opens correctly in LibreOffice, it opens correctly in Collabora. This means excellent ODF support, good OOXML support, and decades of file format compatibility work.

**Lighter than OnlyOffice.** Collabora's Docker deployment is simpler — typically one container (the CODE image) plus a WOPI host like Nextcloud. Resource requirements are lower: 2-4 GB RAM is comfortable for small teams.

**Deep Nextcloud integration.** If you run Nextcloud, Collabora is the path of least resistance. The Nextcloud Office app connects to a Collabora CODE server, and you get full document editing inside your Nextcloud web interface. No separate login, no separate file management.

**Mobile-friendly viewer.** The web interface works on mobile browsers for viewing and light editing. It's not as polished as Google Docs mobile, but it's functional.

**True open-source pedigree.** LibreOffice is one of the oldest and most respected open-source projects. Collabora builds on that foundation with a modern web interface.

### What Collabora Gets Wrong

**OOXML fidelity is good, not great.** Complex `.docx` files — especially those with advanced tracked changes, nested tables, or custom XML — can render differently in Collabora than in Word. For most documents, it's fine. For legal documents with precise formatting requirements, test thoroughly.

**The Docker setup has a learning curve.** Here's a minimal deployment with Nextcloud:

```yaml
version: "3.8"

services:
  collabora:
    image: collabora/code:latest
    container_name: collabora
    ports:
      - "9980:9980"
    environment:
      - extra_params=--o:ssl.enable=false --o:ssl.termination=true
      - username=admin
      - password=your-admin-password
      - server_name=collabora\.yourdomain\.com
      - dictionaries=en_US,es_ES,fr_FR
    cap_add:
      - MKNOD
    restart: unless-stopped
```

Then you configure Nextcloud's Office app to point at `https://collabora.yourdomain.com`. It works, but the `extra_params` environment variable with LibreOffice command-line flags is a reminder that you're running a desktop office suite wrapped in a web server.

**Collaboration is server-mediated.** Like OnlyOffice, the server sees your documents. No E2EE option.

**The web interface feels like LibreOffice in a browser.** This is both a strength and a weakness. If you like LibreOffice, you'll feel at home. If you're used to Google Docs' minimalist interface, Collabora feels cluttered.

**No standalone mobile apps.** Collabora is browser-only on mobile. There's no native iOS or Android app.

### Who Collabora Is For

- **Nextcloud users** who want integrated document editing without adding another service
- **LibreOffice fans** who want a web-based version of their favorite office suite
- **Organizations committed to ODF** as their document standard
- **Teams that need lighter resource usage** than OnlyOffice

## The Head-to-Head Comparison

### Document Editing

| Test | Bento | OnlyOffice | Collabora |
|------|-------|------------|-----------|
| Open complex `.docx` with tracked changes | ❌ | ✅ Excellent | ✅ Good |
| Create new document from scratch | ❌ | ✅ | ✅ |
| Real-time collaborative editing | N/A | ✅ | ✅ |
| Offline editing | ✅ (the whole point) | ❌ | ❌ |
| Mobile editing | ❌ | ⚠️ Basic | ⚠️ View mostly |

**Winner for documents:** OnlyOffice, by a significant margin. Bento doesn't do documents at all. Collabora is solid but OnlyOffice's OOXML fidelity is better.

### Spreadsheets

| Test | Bento | OnlyOffice | Collabora |
|------|-------|------------|-----------|
| Open `.xlsx` with pivot tables | ❌ | ✅ | ✅ |
| Complex formulas | ❌ | ✅ | ✅ |
| Charts and graphs | ✅ (on slides) | ✅ | ✅ |
| Real-time collaboration | N/A | ✅ | ✅ |

**Winner for spreadsheets:** OnlyOffice, again. Bento doesn't do spreadsheets (yet). Collabora's spreadsheet editor is capable but OnlyOffice's feels more responsive with large datasets.

### Presentations

| Test | Bento | OnlyOffice | Collabora |
|------|-------|------------|-----------|
| Create presentation from scratch | ✅ | ✅ | ✅ |
| Open `.pptx` files | ❌ | ✅ | ✅ |
| Morph/advanced transitions | ✅ (native morph) | ⚠️ Basic | ⚠️ Basic |
| Presenter view | ✅ | ✅ | ✅ |
| Export to PDF | ✅ | ✅ | ✅ |
| Self-contained file | ✅ (the file IS the app) | ❌ | ❌ |
| AI slide generation | ✅ First-class | ❌ | ❌ |
| E2EE collaboration | ✅ | ❌ | ❌ |

**Winner for presentations:** Bento, if you're creating new presentations and value portability, privacy, and AI integration. OnlyOffice if you need `.pptx` compatibility and a traditional workflow.

### Deployment Complexity

| | Bento | OnlyOffice | Collabora |
|---|---|---|---|
| **Containers** | 0 | 4 | 1-2 |
| **Database** | None | PostgreSQL | None (stateless) |
| **RAM needed** | 0 (client-side) | 4-8 GB | 2-4 GB |
| **Setup time** | 10 seconds | 30-60 minutes | 15-30 minutes |
| **Updates** | In-app, signed | Docker pull + restart | Docker pull + restart |
| **Backup strategy** | Copy the file | Database dump + volumes | Copy config |

**Winner for deployment:** Bento, by a mile. There's nothing to deploy. OnlyOffice and Collabora are both reasonable Docker deployments, but they're real infrastructure that needs maintenance.

### Privacy & Security

| | Bento | OnlyOffice | Collabora |
|---|---|---|---|
| **Server sees content** | No (E2EE) | Yes | Yes |
| **Offline mode** | ✅ Hard-blocked | ❌ | ❌ |
| **Auditable** | ✅ Single file, view-source | ⚠️ Large codebase | ⚠️ Large codebase |
| **Key management** | In-file, user-controlled | Server-side | Server-side |

**Winner for privacy:** Bento. The E2EE model where the server stores only ciphertext is fundamentally different from OnlyOffice and Collabora's server-mediated collaboration. If you're self-hosting on your own hardware, the practical difference may be small — but the architectural difference is real.

## Can You Actually Replace Google Workspace?

Here's the honest answer, broken down by what you actually use:

### If you mostly use Google Slides → Bento

If presentations are 80% of your Google Workspace usage and you occasionally open a Doc or Sheet, Bento is a genuine upgrade. Your presentations become self-contained files that work forever, on any computer, with E2EE collaboration and AI-native editing. For the occasional document or spreadsheet, keep a free Google account or use LibreOffice locally.

**Migration path:**
1. Download Bento from [bento.page](https://bento.page)
2. Recreate your most-used presentation templates in Bento
3. Export critical Google Slides as PDF for reference
4. Use Bento for all new presentations
5. Keep Google Docs/Sheets for the 20% of work that isn't presentations

### If you use the full Google Workspace → OnlyOffice + Bento

If you live in Docs, Sheets, and Slides daily, OnlyOffice is the closest self-hosted equivalent. It handles documents and spreadsheets with production-grade OOXML compatibility, and its presentation editor is competent. Add Bento for presentations where you want the self-contained file format, E2EE collaboration, or AI integration.

**Migration path:**
1. Deploy OnlyOffice Docker stack (30-60 minutes)
2. Connect it to Nextcloud if you use it, or use OnlyOffice's built-in file management
3. Migrate critical documents and spreadsheets to OnlyOffice
4. Use Bento for new presentations
5. Set up automated backups of the OnlyOffice PostgreSQL database

### If you already run Nextcloud → Collabora

If Nextcloud is your file hub, Collabora is the path of least resistance. The integration is seamless, the resource requirements are lower than OnlyOffice, and you get full document editing without leaving your existing workflow. Add Bento for presentations if you want the self-contained format.

**Migration path:**
1. Deploy Collabora CODE Docker container (15-30 minutes)
2. Install and configure Nextcloud Office app
3. Start creating and editing documents inside Nextcloud
4. Optionally add Bento for presentation-specific workflows

### If you need maximum privacy → Bento + local LibreOffice

If your threat model includes "the server should never see my documents," Bento's E2EE model is the only option for collaborative presentations. For documents and spreadsheets, use LibreOffice locally with Syncthing or a similar peer-to-peer sync tool. This is the most privacy-respecting setup, but it sacrifices real-time collaboration on documents.

## The Stack I'm Actually Running

After a week of testing, here's what I settled on:

- **Bento** for all new presentations. The self-contained file format, E2EE collaboration, and AI integration are genuinely better than anything else available. I've already rebuilt my most-used slide templates.
- **OnlyOffice** for documents and spreadsheets. The OOXML compatibility is too good to pass up when I'm exchanging files with people who use Microsoft Office.
- **LibreOffice** installed locally as a fallback. Sometimes you just need to open a file without spinning up a Docker container.

I'm not running Collabora in production because I don't use Nextcloud as my primary file manager. If I did, I'd probably use Collabora instead of OnlyOffice for the tighter integration.

## The Bottom Line

Bento is not a Google Workspace replacement — and it doesn't try to be. It's a PowerPoint replacement that happens to be the most interesting piece of office software I've seen in years. The single-file architecture, E2EE collaboration, and AI-native design point to a future where office documents are self-contained, privacy-respecting, and agent-friendly.

But that future isn't here yet for documents and spreadsheets. For those, OnlyOffice and Collabora are the battle-tested options, and they're genuinely good. OnlyOffice wins on OOXML compatibility and feature completeness. Collabora wins on resource efficiency and Nextcloud integration.

The real answer to "can you replace Google Workspace with self-hosted tools?" is: **yes, but not with one tool.** You need a combination. And that's fine — the self-hosted philosophy has always been about composing the right tools for your needs, not finding one monolith that does everything.

Bento just made the composition a lot more interesting.

---

*What's your self-hosted office stack? Are you using Bento, OnlyOffice, Collabora, or something else entirely? I'd love to hear about your setup — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [self-hosted calendar tools](/blog/2026-06-26-self-hosted-calendar-tools-homelab) and [running local LLMs on your Mac Mini](/blog/2026-06-12-local-llms-mac-mini-practical-guide).*
