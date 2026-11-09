---
layout: post.njk
title: "Self-Hosted AI News Digest: Turn RSS + Ollama Into Your Own Daily Briefing"
date: 2026-11-09
description: "The internet wants to drown you in headlines. Instead of doomscrolling, build a self-hosted pipeline that fetches your RSS feeds, summarizes them with a local LLM, and hands you one clean morning briefing. No API keys, no feed going to a third party, no subscription. Here's the complete guide with n8n + Ollama, plus the open-source projects already doing it."
tags: ["rss", "ai", "ollama", "n8n", "news-digest", "self-hosted", "homelab", "automation", "local-llm", "aihot", "summarization"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-09-self-hosted-ai-news-digest/"
affiliate: false
cta: true
---

There are two kinds of mornings. The kind where you open a feed reader and get forty unread items you'll never actually read. And the kind where you open one message and get forty items already triaged, deduplicated, and summarized into something a human can absorb in ninety seconds.

The first kind is what RSS gives you by default. The second kind is what an **AI news digest** gives you — and it's a problem a lot more interesting than "build an RSS reader," because the reading part has been solved a hundred times over. The *generation* part — the step where a machine reads everything so you don't have to — is still wide open, especially if you want to run it yourself.

This post is the guide I wish existed when I built mine. I'll show you two paths: the open-source projects that already do this out of the box (led by **AIHOT**, sitting at roughly ~9.9k stars), and the roll-your-own pipeline using **n8n + Ollama** that gives you full control over exactly what "news" means to you and how it gets summarized. No cloud API keys, no sending your reading list to anyone, no per-token billing — just a local LLM chewing through feeds overnight and leaving a briefing on your nightstand.

---

## Why "AI News Digest" Is a Real Gap

Here's the thing that surprised me when I went looking: there are *dozens* of self-hosted RSS readers. FreshRSS, Miniflux, Tiny Tiny RSS, Reeder, NetNewsWire, yarr, newsboat — the category is saturated. What there is **not** a lot of is tooling that sits on top of those readers and turns a pile of items into *an opinion*.

The distinction matters. A reader is a list. A digest is a *judgment*: "these five things mattered today, here's why, here's the common thread, here's what you can ignore."

That judgment layer is exactly what a local LLM is good at. And it's a genuinely low-competition topic — the search cluster around "ai news digest" is rich (skills, agents, apps, GitHub repos, Reddit threads all circling the same idea) but the *self-hosted generation* angle is still thin. Most tutorials stop at "here's how to install a feed reader," as if the hard part were parsing XML. It's not. The hard part is the summarization, deduplication, and prioritization — and that's the part that's finally easy now that a decent LLM runs on a $600 Mac Mini or any spare box with a GPU.

---

## The Anatomy of an AI News Digest

Before I hand you code, let's be clear about what the pipeline actually does, because if you understand the pieces you can rebuild it with any tool. Every AI news digest — from the polished SaaS ones to my janky cron job — is four stages:

1. **Fetch.** Pull new items from a list of RSS/Atom feeds. This is the only part your feed reader already does.
2. **Filter & dedupe.** Drop the noise, merge stories that ten outlets all wrote about, and decide what's actually worth the model's attention. This is where most homegrown digests fall apart — if you summarize *every* item you just get a summary of spam.
3. **Summarize.** Run each surviving item (or a batched group of them) through an LLM with a tight prompt: what happened, why it matters, one or two sentences, no fluff.
4. **Deliver.** Write the result to a file, send it to your phone, drop it in a Telegram channel, or render it as an email. Something you'll actually read.

That's it. Four steps. The magic is that steps 2 and 3 — the two that used to require a room full of grad students or a paid API — now run locally, overnight, for the cost of electricity.

---

## Path 1: The Open-Source Projects (Start Here)

Before you build anything, check whether one of these already does 80% of what you want. Building is fun, but standing on shoulders is faster.

### AIHOT (~9.9k stars)

**[AIHOT](https://github.com/we0h/AIHOT)** is the anchor project in this space and the first thing I'd point you at. It's a full-stack "AI hot topics" aggregator: it pulls in news from multiple sources, uses AI to cluster and summarize them, and presents a clean ranked feed of what's actually trending — not a chronological firehose.

What I like about it:
- **It's a *product*, not a library.** You get a web UI, trending topics, AI summaries, and source clustering out of the box.
- **Actively maintained** with a real community, which matters when you're depending on it to wake up and digest every morning.
- **Good architecture to steal from** even if you don't run it verbatim — its source-clustering and dedup logic is worth reading.

The tradeoff: it's opinionated about its UI and its source list, and historically it's leaned on AI APIs (though the recent versions have gotten friendlier about plugging in a local model). If you want a turnkey trending-news digest and don't mind tinkering with its config, this is your fastest route to "morning briefing" without writing a line of code.

### The wider field

AIHOT isn't alone. The "ai news digest" cluster spans a bunch of related projects worth knowing about, even if I don't run them all:

- **Hacker-News-style digest bots** — there are several small projects that take the HN front page (or a specific topic) and summarize it daily with a local model. Great pattern to copy even if you don't care about HN.
- **The skill/agent variants** — people have packaged "summarize my feeds" as a reusable agent skill or an n8n template, which is convenient but usually assumes a cloud model.
- **Reddit/Twitter digest tools** — same idea, different sources. They demonstrate that the *generation* layer is source-agnostic; swap the inputs and you get a totally different digest.

The common thread: everyone solves fetch+deliver easily, and everyone struggles with filter+summarize. Which is exactly why I eventually rolled my own — because I wanted the filter step to be *mine*, not a project maintainer's best guess at what I care about.

---

## Path 2: Roll Your Own with n8n + Ollama

If you want full control — your sources, your noise filter, your summary style, your delivery — here's the pipeline I actually run. It's an n8n workflow that fires on a schedule, talks to a local Ollama instance, and writes a Markdown briefing to disk. The whole thing costs nothing and sends nothing off-box.

### Prerequisites

- **Docker** (or a host running n8n and Ollama directly)
- **n8n** — self-hosted, so your workflow and your data stay home
- **Ollama** — serving a model that's decent at summarization. On my Mac Mini I use a small-to-mid model (`qwen3` or a 7–14B class model); you don't need a frontier model to summarize headlines. A 7B model does this job well and runs fast.
- A handful of feeds you actually care about.

### Step 1: Stand up Ollama

```bash
# Pull a summarization-friendly model (7–14B hits the sweet spot)
ollama pull qwen3:8b
ollama serve
```

Verify it's up:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:8b",
  "prompt": "Summarize this in one sentence: ' +
    '"Self-hosted AI tools grew 40% in 2026 as homelabbers embraced local models."',
  "stream": false
}'
```

### Step 2: Stand up n8n

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  --add-host=host.docker.internal:host-gateway \
  n8nio/n8n
```

Note the `--add-host` flag — it lets the n8n container reach Ollama running on your host via `host.docker.internal:11434`. If you run n8n natively (not in Docker), just use `localhost:11434`.

### Step 3: Build the workflow

In the n8n editor, create a new workflow and add these nodes:

1. **Schedule Trigger** — set it to fire daily at, say, 06:30, or hourly if you're impatient.
2. **RSS Read** — add one per feed, or use a single **Code** node to loop over your feed list (cleaner if you have more than three feeds).
3. **Code (filter/dedupe)** — this is the step everyone skips and then regrets. Strip HTML, drop items older than 24h, drop items whose titles match a keyword blocklist, and group items by a rough similarity score so you don't summarize the same story ten times.
4. **HTTP Request → Ollama** — POST to `http://host.docker.internal:11434/api/chat` (or `/api/generate`) with a tight system prompt and the batched item titles + snippets as the payload.
5. **Write Binary File** (or a **Code** node) — save the resulting Markdown to a path your phone or a later step can read.
6. **Telegram / Email / ntfy** node — deliver the briefing to wherever you'll actually read it.

The Ollama call is the heart of it. Here's the prompt shape I use:

```json
{
  "model": "qwen3:8b",
  "stream": false,
  "messages": [
    {
      "role": "system",
      "content": "You are a news editor. Given a list of headlines and snippets, " +
        "produce a Markdown briefing: 1) the 5 most important stories with a " +
        "one-sentence 'why it matters', 2) a one-line 'themes today' section, " +
        "3) a short 'safe to skip' list. Be terse. No fluff. No restating the headline."
    },
    {
      "role": "user",
      "content": "<JSON of the deduped items from step 3>"
    }
  ]
}
```

### Step 4: The dedup filter (the actual hard part)

The summarization is the easy part — any model can summarize. The part that separates a digest you read from a digest you delete is **filtering**, and it happens *before* the model ever sees the items. Here's a minimal filter in a n8n Code node:

```javascript
// items = input from your RSS Read nodes, flattened
const DAY = 24 * 60 * 60 * 1000;
const BLOCKLIST = /(sponsored|press release|advertorial|giveaway)/i;

const seen = new Set();
const filtered = [];

for (const item of items) {
  const json = item.json;
  const age = Date.now() - new Date(json.pubDate || json.isoDate).getTime();
  if (age > DAY) continue;                    // too old
  if (BLOCKLIST.test(json.title)) continue;   // obvious noise

  // crude dedup: key on first 5 normalized words of the title
  const key = json.title
    .toLowerCase()
    .replace(/[^a-z0-9 ]/g, '')
    .split(' ')
    .slice(0, 5)
    .join(' ');
  if (seen.has(key)) continue;                // likely same story
  seen.add(key);

  filtered.push({ title: json.title, snippet: (json.contentSnippet || '').slice(0, 240) });
}

return filtered.map(f => ({ json: f }));
```

This is deliberately crude — five words is not a real similarity metric — but it catches the overwhelming majority of duplicate coverage ("Nvidia unveils..." / "Nvidia announces..." collapse into one). If you want real clustering, embed the titles and cosine-compare them; for a personal digest, the crude version gets you 90% of the way for 2% of the effort.

---

## The Honest Tradeoffs

Let me be straight about the costs, because "run an AI news digest" is easy to romanticize and easy to abandon:

- **A 7B model is not a journalist.** It will summarize faithfully but it will not tell you *why this matters to you specifically*. It has no memory of what you care about across days. That "why it matters" is generic, and after a week of it you'll notice. If you want personalized judgment, you need to feed the model your own context (past briefings, your saved articles, a note of "I work in X, I care about Y") every single run.
- **Garbage in, garbage out — always.** If your feeds are noisy, your digest is noisy, and no amount of prompt engineering fixes that. Spend real time curating the feed list. Thirty good feeds beats three hundred.
- **Hallucination is a real risk, not a boogeyman.** A model will occasionally merge two unrelated stories or attribute a claim to the wrong company. For a personal briefing that's mostly harmless (you're not publishing it), but it means you should treat the digest as a *pointer* to go read the real thing, not as ground truth.
- **It's one more thing to maintain.** n8n updates, Ollama model pulls, a feed URL going stale and silently returning nothing. Budget for occasional upkeep, or it'll rot.
- **The "safe to skip" list is the killer feature.** Most digest tools over-index on "here's what happened" and under-index on "here's what you can ignore." The ignore list is what actually saves you time. Make sure your prompt produces it.

None of this should stop you. It just sets the expectation: this is a *triage* tool, not a replacement for reading. It's the difference between opening a feed reader and opening a briefing — and that difference is bigger than it sounds.

---

## The Bottom Line

RSS solved the *fetching* problem twenty years ago, and self-hosting solved the *reading* problem a decade ago. What's new — and what's still wide open — is the **generation** layer: a machine that reads your feeds, throws away the noise, and hands you a judgment every morning.

You have two ways in. If you want it today, run **AIHOT** (or one of its kin) and accept its opinions about what "trending" means. If you want the filter to be *yours*, build the n8n + Ollama pipeline above — it's four stages, maybe an afternoon of work, and it costs nothing but electricity. Either way, the local LLM on your Mac Mini or your homelab box is the engine that finally makes the digest real, and it does it without your reading list ever leaving your network.

The whole point of self-hosting was never just "own your data." It was "own your *attention*." An AI news digest is that principle taken to its logical end: not reading everything, not reading nothing, but reading *the right five things* — and knowing, with confidence, that the other thirty-five can wait.

---

**Related posts:**
- [Running Local LLMs on Your Mac Mini: A Practical Guide](/blog/2026-06-12-local-llms-mac-mini-practical-guide/)
- [11 Best n8n Alternatives for Self-Hosted Workflow Automation](/blog/2026-04-26-n8n-alternatives-review/)
- [LocalAI vs Ollama: Which Local LLM Runtime Wins in 2026?](/blog/2026-06-18-localai-vs-ollama-2026/)
- [Self-Hosted LLM Gateway: LiteLLM vs OpenRouter](/blog/2026-11-06-self-hosted-llm-gateway-lite-llm-vs-openrouter/)

---

*Links: [AIHOT](https://github.com/we0h/AIHOT) · [Ollama](https://ollama.com) · [n8n](https://n8n.io) · [FreshRSS](https://github.com/FreshRSS/FreshRSS) · [Miniflux](https://miniflux.app)*
