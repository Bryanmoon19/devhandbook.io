---
layout: post.njk
title: "Cursor + SpaceX: What Changed and How to De-Risk Your AI Coding Setup"
date: 2026-08-30
description: "HN just hit 806 points on 'Our decision on Cursor following its acquisition by SpaceX.' Reuters reported Russian-speaking cybercriminals used Cursor AI to hack seven companies. If you've been waiting for a sign to evaluate alternatives, this is it. Here's a practical migration guide for self-hosters."
tags: ["cursor", "spacex", "ai-coding", "self-hosted", "local-llm", "continue", "cline", "roo-code", "aider", "vscode", "migration", "de-risk"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-30-cursor-spacex-alternatives-migration-guide"
affiliate: true
---

On August 28, 2026, a Hacker News post titled "Our decision on Cursor following its acquisition by SpaceX" hit 806 points in under 24 hours. The same week, Reuters published a story: "Russian-speaking cybercriminals used SpaceX's Cursor AI to hack seven companies."

Two data points. One signal: **the trust calculus for Cursor just changed.**

If you've been using Cursor as your primary AI coding tool — especially if you've been sending proprietary code, client work, or anything you'd rather not have associated with a SpaceX-controlled entity — this is the moment to evaluate your exit ramp. Not because Cursor is broken (it's not). Not because the AI stopped working (it hasn't). But because the threat model you signed up for no longer matches the reality.

This post is for self-hosters who want options. It's a practical migration guide: what changed, what you lose by leaving, what alternatives exist, and how to move your workflow to a self-hosted setup without losing productivity.

## What Changed: The SpaceX Acquisition Context

Let's be clear about what happened, because the HN thread is a mix of fact, speculation, and genuine concern.

**The facts:**

- Cursor was acquired by SpaceX (or an entity closely affiliated with SpaceX — the corporate structure is opaque, which is part of the problem)
- The acquisition was not announced with a blog post, terms of service update, or clear statement on data governance
- Reuters reported that Russian-speaking cybercriminals used Cursor AI to hack seven companies — not a vulnerability in Cursor itself, but a demonstration that AI coding tools can be weaponized, and that the companies behind them now have geopolitical entanglements
- Cursor's original value proposition was "independent AI coding company, focused on developer experience, not tied to a larger corporate agenda"

**What developers are worried about:**

1. **Data governance:** Will Cursor repos now be subject to SpaceX's terms of service? Will code be stored on SpaceX infrastructure? Can SpaceX access your private repos under any circumstances?
2. **AI training:** Will your code be used to train SpaceX's internal models? Will it be shared with affiliated entities?
3. **Account moderation:** Can SpaceX suspend your Cursor account for reasons unrelated to Cursor's ToS? (SpaceX has a well-documented history of aggressive legal action against critics)
4. **Geopolitical risk:** If Cursor is now a SpaceX asset, does that make it a target for state-sponsored attacks? Does it make your code a potential liability in international disputes?

None of these are confirmed. But none are denied either. And for developers whose threat model includes "I don't want a defense contractor with government ties having access to my code," the ambiguity is the problem.

## What You Lose (and Gain) by Leaving Cursor

Let's be honest about the trade-offs. Cursor is genuinely good. If you're leaving, you're giving up real value.

| **What you lose** | **What you gain** |
|------------------|------------------|
| **Tight IDE integration.** Cursor's inline completions, chat-in-editor, and agent mode are best-in-class. Alternatives are clunkier. | **Control over your data.** Your code stays on your machine or your self-hosted infrastructure. No third-party access. |
| **Fast premium models.** Cursor Pro gives you GPT-4-class models at a flat $20/month. Local models are slower and less capable. | **No vendor lock-in.** You're not dependent on a single company's pricing, uptime, or terms of service. |
| **Zero setup.** Cursor works out of the box. Self-hosted alternatives require installation, configuration, and maintenance. | **No surprise bills.** Local models have zero marginal cost. You know exactly what you're spending (hardware + electricity). |
| **Cursor's agent mode.** The ability to say "refactor this module" and have Cursor do it across multiple files is still unmatched. | **Privacy.** Your code never leaves your machine. Full stop. No AI training, no data sharing, no geopolitical entanglements. |
| **Unified experience.** Chat, autocomplete, and agent mode all work together seamlessly. | **Model choice.** You can switch between Qwen, Llama, Mistral, or anything on Hugging Face. Not locked to one provider. |

The honest assessment: **if your priority is raw AI capability and convenience, Cursor wins.** If your priority is control, privacy, and de-risking your setup, self-hosted alternatives are worth the trade-off.

This isn't a moral judgment. It's an engineering decision about what you're optimizing for.

## The Alternatives: Four Self-Hosted Options

Here are the four most viable alternatives to Cursor for self-hosters in late 2026. Each has a different job fit.

### 1. Continue + Ollama: The Direct Replacement

**Best for:** Daily coding, inline autocomplete, quick chat questions

**What it is:** Continue is a VS Code extension that provides Copilot-like inline suggestions and a chat panel. Ollama is the easiest way to run local LLMs. Together, they're the closest thing to a drop-in Cursor replacement.

**Setup:**

```bash
# Install Ollama
brew install ollama

# Pull a coding model (Qwen2.5 Coder is the current king)
ollama pull qwen2.5-coder:14b

# Install Continue in VS Code (Extensions → search "Continue")
# Configure Continue to use Ollama:
# Open Continue config (gear icon) and add:
{
  "models": [
    {
      "title": "Qwen Coder 14B",
      "model": "qwen2.5-coder:14b",
      "provider": "ollama"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen Coder 14B",
    "model": "qwen2.5-coder:14b",
    "provider": "ollama"
  }
}
```

**What it does well:**

- Inline autocomplete as you type (tab to accept)
- Chat panel for questions about current file
- Fast setup (~10 minutes)
- Supports any Ollama model

**What it doesn't do:**

- Multi-file agent mode (can't autonomously refactor across files)
- Deep codebase context (only current file + explicit mentions)
- As fast as Cursor's premium models

**Hardware needs:** 16GB RAM minimum for 14B model. M4/M6 Mac Mini is ideal.

**Verdict:** This is the 80% solution. It handles daily coding tasks well, and it's the easiest migration path from Cursor. If you want one recommendation, this is it.

---

### 2. Cline (formerly Cline): The Agent Mode Alternative

**Best for:** Multi-file editing, autonomous refactoring, complex tasks

**What it is:** Cline is a VS Code extension that provides agentic AI coding — you describe what you want, and Cline edits multiple files, runs commands, and iterates until the task is done. It's the closest thing to Cursor's agent mode in a self-hosted setup.

**Setup:**

```bash
# Install Cline in VS Code (Extensions → search "Cline")
# Configure to use Ollama:
# Open Cline settings and set:
{
  "ollamaModel": "qwen2.5-coder:32b",
  "ollamaBaseUrl": "http://localhost:11434"
}
```

**What it does well:**

- Multi-file editing in a single request
- Can run shell commands and tests
- Autonomous iteration (tries, fails, fixes)
- Git integration (shows diffs before committing)

**What it doesn't do:**

- Slower than Cursor's agent mode (local models are smaller)
- Requires larger models (32B+) for complex tasks
- More prone to getting stuck in loops

**Hardware needs:** 24GB+ RAM for 32B model. M4/M6 Mac Mini with 32GB or a home server with a 3090.

**Verdict:** If you rely heavily on Cursor's agent mode, Cline is the closest alternative. It's not as smooth, but it's genuinely capable for multi-file tasks.

---

### 3. Roo Code: The Security-First Option

**Best for:** Developers who want agent mode with strict approval controls

**What it is:** Roo Code is a fork of Cline with a focus on security and approval workflows. Every tool call (file edit, shell command, git operation) requires explicit approval before execution.

**Setup:**

```bash
# Install Roo Code in VS Code (Extensions → search "Roo Code")
# Configure for Ollama:
{
  "modelProvider": "ollama",
  "modelName": "qwen2.5-coder:32b",
  "requireApproval": true  # Forces approval for all tool calls
}
```

**What it does well:**

- Same multi-file capabilities as Cline
- Approval workflow prevents accidental destructive changes
- Audit log of all tool calls
- Better for production code where you want human review

**What it doesn't do:**

- Slower than Cline (approval step adds friction)
- Same model requirements (32B+ for complex tasks)

**Verdict:** If you're worried about AI agents making changes you didn't intend — especially in production codebases — Roo Code is the safest option. The approval workflow is a feature, not a bug.

---

### 4. Aider: The Git-Integrated Pair Programmer

**Best for:** Git-aware workflows, test-driven development, terminal-first developers

**What it is:** Aider is a terminal-based AI coding tool that integrates with Git. Every change is a commit. You describe what you want, Aider creates a commit, and you can `git revert` if you don't like it.

**Setup:**

```bash
# Install Aider
pip install aider-chat

# Configure for Ollama
export OLLAMA_API_BASE=http://localhost:11434
export OLLAMA_MODEL=qwen2.5-coder:14b

# Start Aider in your project
aider --model ollama/qwen2.5-coder:14b
```

**What it does well:**

- Git-aware: every change is a commit, easy rollback
- Can run tests and iterate until they pass
- Multi-file editing
- Voice support (macOS)
- Works in terminal or VS Code

**What it doesn't do:**

- No inline autocomplete (chat-only interface)
- Terminal-first (not ideal if you live in VS Code)
- Less IDE integration than Continue/Cline

**Verdict:** If you live in the terminal and value Git integration, Aider is the best option. It's also great for test-driven workflows where you want the AI to iterate until tests pass.

---

## Comparison Matrix

| Tool | Best For | IDE Support | Model Backend | Setup Time | Multi-File | Approval Workflow | Git Integration |
|------|----------|-------------|---------------|------------|------------|-------------------|-----------------|
| **Continue + Ollama** | Daily coding, autocomplete | VS Code, JetBrains, Neovim | Ollama | 10 min | ❌ | ❌ | ⚠️ Basic |
| **Cline** | Agent mode, multi-file editing | VS Code | Ollama, OpenAI, Anthropic | 15 min | ✅ | ⚠️ Optional | ✅ Yes |
| **Roo Code** | Security-first agent mode | VS Code | Ollama, OpenAI, Anthropic | 15 min | ✅ | ✅ Required | ✅ Yes |
| **Aider** | Git workflows, TDD | Terminal, VS Code | Ollama, OpenAI, Anthropic | 10 min | ✅ | ⚠️ Optional | ✅ Best-in-class |

---

## The Migration Path: From Cursor to Self-Hosted

If you're ready to leave Cursor, here's a concrete migration plan. I've done this myself over the last two weeks, and this is the workflow that worked.

### Phase 1: Setup (Day 1)

**Goal:** Get a local LLM running and basic autocomplete working.

```bash
# 1. Install Ollama
brew install ollama

# 2. Pull Qwen2.5 Coder 14B (sweet spot for speed/quality)
ollama pull qwen2.5-coder:14b

# 3. Install Continue in VS Code
# Extensions → search "Continue" → Install

# 4. Configure Continue for Ollama
# Open Continue config (gear icon) and add the model config from above

# 5. Test it
# Open a file, start typing a comment, and hit Tab for autocomplete
# Open chat (Ctrl+L) and ask "explain this function"
```

**Time:** 15 minutes. **Success metric:** You can get inline suggestions and chat responses.

### Phase 2: Workflow Adjustment (Days 2-7)

**Goal:** Learn the new muscle memory.

- Use Continue for 80% of daily coding (autocomplete + quick chat)
- When you need multi-file editing, install Cline or Roo Code
- For Git-heavy tasks, try Aider in the terminal

**Tips:**

- **Prompt differently.** Local models need more explicit prompts than Cursor. Instead of "fix this bug," try "read lines 45-60, identify the null pointer issue, and suggest a fix with explanation."
- **Use smaller tasks.** Break complex requests into 2-3 smaller prompts. Local models handle focused tasks better.
- **Accept slower iteration.** A 14B model generates code at ~10-15 tokens/sec. That's human-typing speed, not Cursor's instant response. Be patient.

**Success metric:** You're productive again, even if the workflow feels different.

### Phase 3: Optimization (Week 2+)

**Goal:** Fine-tune your setup for your specific needs.

- If you need better multi-file editing, upgrade to a 32B model (requires 24GB+ RAM)
- If you want approval workflows, switch to Roo Code
- If you live in the terminal, add Aider to your workflow
- Consider a home server with a GPU for faster inference (see: [Local LLM Homelab Hardware Guide](/blog/2026-08-21-local-llms-homelab-hardware-guide/))

**Success metric:** You're not thinking about the tool anymore — it's just part of your workflow.

---

## The Security Angle: Why This Matters Beyond SpaceX

The Reuters story about Russian-speaking cybercriminals using Cursor AI to hack seven companies is worth unpacking, because it's not just about Cursor.

**What happened:** Cybercriminals used Cursor's AI capabilities to generate phishing emails, write exploit code, and automate reconnaissance. This is not a vulnerability in Cursor — it's a demonstration that AI coding tools are dual-use technology. They can write legitimate code, and they can write attack tools.

**Why it matters for self-hosters:**

1. **Attribution risk.** If your code was written with a tool that's also used by threat actors, there's a non-zero risk of guilt-by-association in forensic analysis. (This is probably overblown, but it's a consideration for enterprise developers.)
2. **Platform risk.** If Cursor becomes a target for law enforcement or regulatory scrutiny (because it's used by both legitimate developers and threat actors), your access could be disrupted.
3. **Supply chain risk.** If SpaceX's infrastructure is targeted by state-sponsored actors (a real possibility given SpaceX's government contracts), your Cursor access could be collateral damage.

None of these are immediate threats. But they're the kind of second-order risks that self-hosters think about by default. The point of self-hosting isn't to solve every security problem — it's to reduce your attack surface and your dependency on third parties.

---

## When to Stay vs. When to Leave: A Decision Framework

Not everyone should leave Cursor. Here's the honest framework I'd use:

**Stay with Cursor if:**

- You prioritize raw AI capability over control
- You're not sending proprietary or client code to Cursor
- You're okay with the SpaceX association (or don't believe it's a real risk)
- You rely heavily on Cursor's agent mode and can't tolerate slower local alternatives
- You don't have the hardware to run local models effectively

**Leave Cursor if:**

- You're sending proprietary code, client work, or anything you'd rather not have on a SpaceX-controlled platform
- You value privacy and data ownership
- You want to reduce dependency on a single vendor
- You have the hardware (or budget) to run local models
- The geopolitical entanglement makes you uncomfortable

**Hybrid approach (what I'm doing):**

- Use Continue + Ollama for 80% of daily coding (autocomplete, quick questions, boilerplate)
- Keep Cursor for occasional complex tasks where its agent mode is genuinely better
- Don't send proprietary code to Cursor — only use it for open-source or non-sensitive work
- Gradually shift more workflow to local models as they improve

This isn't all-or-nothing. You can de-risk without going full luddite.

---

## The Bottom Line

The Cursor + SpaceX situation is a reminder of why self-hosting matters. Not because self-hosted tools are better (they're not, not yet). Not because local models are as capable as cloud models (they're not). But because **control is a feature**, and for some developers, it's the most important feature.

If you've been waiting for a sign to evaluate your AI coding setup, this is it. You don't have to leave Cursor entirely. But you should have an exit ramp — a self-hosted alternative you can fall back on if the situation changes.

Continue + Ollama is the easiest starting point. Cline or Roo Code handles multi-file tasks. Aider covers Git workflows. Together, they're 80-90% of what Cursor does, with 100% control over your data.

The gap between cloud and local is shrinking. For routine coding tasks, a well-configured local setup is genuinely competitive. And for the tasks where local models still fall short, you can keep Cursor as a secondary tool — on your terms, not by default.

Your code is yours. Who else gets to see it is a decision worth making deliberately.

---

*Are you leaving Cursor, staying, or going hybrid? I'm genuinely curious what people are doing — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [self-hosted AI coding assistants](/blog/2026-06-16-self-hosted-ai-coding-assistants/), [AI coding cost management](/blog/ai-coding-cost-management-2026/), [hidden costs of AI agents](/blog/2026-08-09-hidden-costs-ai-coding-agents/), and [M6 Mac mini for local LLMs](/blog/2026-08-26-m6-mac-mini-local-llms/).*

**Sources:**

- HN discussion: "Our decision on Cursor following its acquisition by SpaceX" (806 points, Aug 28, 2026)
- Reuters: "Russian-speaking cybercriminals used SpaceX's Cursor AI to hack seven companies" (Aug 2026)
