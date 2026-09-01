# CursorExit — Promo Posts (Draft, ready to post)

**Target window:** This week, while the SpaceX acquisition news is warm (HN 806 pts, Aug 28).
**URL to promote:** https://devhandbook.io/cursorexit/
**Companion guide:** https://devhandbook.io/blog/2026-08-30-cursor-spacex-alternatives-migration-guide/

---

## 1. Show HN (Hacker News)

**Title:** Show HN: CursorExit — find your Cursor replacement in 30 seconds

**Body:**

Cursor got acquired by SpaceX. Everyone's asking the same question: *should I leave, and what do I switch to?*

So I built a 30-second quiz that answers it. You tell it how you actually use Cursor (agentic coding, autocomplete, chat, scripting), whether you want local models or a cloud API, your setup tolerance, and budget — it scores 7 tools (Continue, Cline, Roo Code, Aider, Zed, OpenHands, or staying on Cursor) and gives you ONE recommendation with honest tradeoffs.

The part I care about: every result includes a "what you give up vs. Cursor" section. Generic listicles rank 10 tools and call it a day. This tells you what you actually lose — because switching from Cursor isn't free, and pretending otherwise is how people bounce back a week later.

Built for the self-hosted crowd: local-model support (Ollama), no backend, static page, deploys on Cloudflare Pages. The scoring matrix is a JSON file — easy to extend with new tools.

Try it: https://devhandbook.io/cursorexit/

Full migration guide with copy-paste setup for each tool: https://devhandbook.io/blog/2026-08-30-cursor-spacex-alternatives-migration-guide/

Would love feedback on the scoring — especially from people who've actually made the switch. What did I get wrong about your tool of choice?

---

## 2. r/selfhosted

**Title:** I built a quiz that tells you which self-hosted Cursor replacement fits your setup

**Body:**

With the SpaceX acquisition, a lot of people are suddenly asking "what do I switch to from Cursor?" — and the answer depends a lot on how you actually use it.

I made a 30-second picker that scores 7 options (Continue, Cline, Roo Code, Aider, Zed, OpenHands, or staying) against your answers: agentic vs autocomplete vs chat, local model vs cloud API, setup tolerance, budget.

The self-hosted angle is the whole point — most of these run fully local via Ollama, so your code never leaves your machine. Every result card also shows the honest "what you lose vs. Cursor" tradeoff, because switching isn't free and I don't want to pretend it is.

https://devhandbook.io/cursorexit/

Companion guide with actual setup commands (Ollama + Continue, Cline, etc.): https://devhandbook.io/blog/2026-08-30-cursor-spacex-alternatives-migration-guide/

Built as a static page, no backend, no tracking beyond GA. The scoring matrix is a JSON file if you want to fork the idea.

---

## 3. r/LocalLLaMA

**Title:** Cursor alternatives that run fully local — a picker for the "own your model" crowd

**Body:**

If the SpaceX acquisition made you want your code to never leave your machine, the good news is the local-LLM path is more viable than ever. Qwen2.5 Coder 14B/32B via Ollama handles daily autocomplete and chat fine on a 16GB+ machine.

I built a 30-second quiz that recommends a Cursor replacement based on how you work — and it's weighted toward local-model support. Continue + Ollama for the drop-in replacement, Cline for agentic multi-file work, Aider for terminal/git-native flow.

https://devhandbook.io/cursorexit/

Setup guide with the exact Ollama configs: https://devhandbook.io/blog/2026-08-30-cursor-spacex-alternatives-migration-guide/

What's your current local coding stack? I'm curious what models people are actually running day-to-day.

---

## 4. r/Cursor

**Title:** Leaving Cursor? Here's a 30-second quiz to find your replacement (honest tradeoffs included)

**Body:**

Post-acquisition, a lot of us are weighing whether to stay. I built a quick picker that asks how you use Cursor and recommends an alternative — or tells you honestly that staying is the right call for your use case.

It's not a "Cursor is bad" post. It scores 7 options and every result includes what you'd actually give up. If you're on the fence, it's a useful 30 seconds.

https://devhandbook.io/cursorexit/

---

## Posting notes

- **HN:** Post between 8–11am ET on a weekday for max visibility. Use the Show HN title verbatim.
- **Reddit:** r/selfhosted and r/LocalLLaMA are the highest-intent for the affiliate angle (they're the ones who'll click a Hetzner/Cloudflare link to self-host). r/Cursor is the biggest refugee pool but lowest affiliate intent.
- **Don't spam all 4 in one day.** Space them: HN + r/selfhosted day 1, r/LocalLLaMA day 2, r/Cursor day 3.
- **Disclosure:** The quiz page already has an affiliate disclosure line. Keep it — Reddit mods and HN both respect it.
- **Source credit:** The migration guide already links back to the HN thread and Reuters. Keep that.
