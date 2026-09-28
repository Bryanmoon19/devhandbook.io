---
layout: post.njk
title: "Your AI Can Now Read Your Bank Account — and a Banker's Take on Why That Should Terrify You (a Little)"
date: 2026-09-28
description: "bankmcp is a 264-star, self-hosted, read-only MCP server that lets Claude, ChatGPT, or Ollama read your bank accounts over open banking. I'm a self-hoster and a banker, so here's what it is, how it works, what I actually worry about when you wire AI into money, and the Docker setup to run it yourself."
tags: ["bankmcp", "mcp", "open-banking", "psd2", "self-hosted", "ai", "claude", "ollama", "personal-finance", "security", "homelab", "docker", "enable-banking"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-09-28-your-ai-can-read-your-bank-account-bankmcp/"
affiliate: true
cta: true
---

There's a line I can't fully cross in my head, and I want to be honest about it up front.

I spend my days working in a bank. I've seen what fraud looks like from the inside — the disputed transactions, the compromised credentials, the customer who handed over their login because a "support" page looked right. And I spend my nights running a homelab full of self-hosted services, writing about MCP servers and AI agents, pushing the exact tools that this site is built around.

Those two people — the banker and the self-hoster — usually don't talk to each other. This week they have to, because **bankmcp** just crossed 260 stars on GitHub with a one-line pitch that's impossible to ignore:

> *"Your AI now reads your bank."*

It's a self-hosted, read-only MCP server that connects your bank accounts to Claude, ChatGPT, Cursor, or a local Ollama model over open banking. And the reason I can't write a normal "here's how to install it" post is that the part of me that works in finance can't stop asking a different question than the one most tutorials answer.

Most tutorials ask: *"How do I make this work?"*

I keep asking: *"What is the absolute worst thing that happens if this goes wrong — and who eats the loss?"*

So this is both posts at once. What bankmcp is and how to run it, *and* the things a banker actually worries about when you wire an LLM into your money. Because the two turn out to be the same story.

## What bankmcp Actually Is

bankmcp is not a bank, and it's not a service. It's a small TypeScript server — an `npm` package called `bankmcp` — that you host yourself. It's MIT-licensed, and the authors run nothing for anyone. There's no hosted version, no account to sign up for, and no third party holding your data.

What it does is sit in the middle of a chain that looks like this:

```
Your assistant ──OAuth──▶ your bankmcp server ──JWT──▶ Enable Banking ──PSD2──▶ your bank
```

Three links, and only one of them is actually on your machine.

- **Your assistant** — Claude, ChatGPT, Cursor, Ollama, or any MCP client — talks to your server as a connector. You sign in once with a password; tokens handle the rest.
- **Your bankmcp server** — holds the Enable Banking application key, your bank consents, and your account IDs. It does *not* store balances or transactions, and it sends no telemetry.
- **Enable Banking** — a licensed open-banking provider that wraps 2,700+ European banks in one PSD2 API. This is the one hop that is not on your machine, and it's the part that makes this whole thing legal.

The key word in the pitch is **read-only.** bankmcp exposes tools for reading balances, listing accounts, and pulling transactions. There are no payment tools — the project is explicit that payments require a licensed PISP and a completely different security model, so they're out of scope. You can ask it:

- *"Has the invoice from Acme been paid?"*
- *"What did I spend on groceries in August?"*
- *"Which subscriptions am I paying for, and what do they cost per year?"*
- *"Tell me when my balance drops below 5,000."*

That last one — a *watch* — is where it gets genuinely useful. bankmcp has a background watcher that fires rules against your transactions and pushes a notification to a webhook. It's the first MCP server I've seen that's genuinely built for the "agent that keeps an eye on my money" use case, not just the "agent I ask a question and it answers" use case.

## How It Works Under the Hood

The architecture is smarter than most MCP servers, and I want to call that out because it's where a lot of the security thought went.

Your server is a **complete OAuth 2.1 authorization server with one user.** Discovery, dynamic client registration, and PKCE come from the MCP SDK. Tokens are stored hashed. Five wrong passwords lock an address out for fifteen minutes. Every successful sign-in is logged — and if you set a `NOTIFY_WEBHOOK_URL`, every sign-in gets sent to you as a message. *A sign-in you didn't make is your alarm.*

There are two ways to run it:

**On your own machine** — for Claude Desktop, Claude Code, Cursor, and other desktop clients. Nothing to deploy, no password. State lives in `~/.bankmcp`, and the bank connection still goes through Enable Banking.

**On a server** — for claude.ai, your phone, or anything that needs a public HTTPS address. This is where the Docker image comes in, published on every release as `ghcr.io/noskillish/bankmcp`.

The state is a single JSON file in `DATA_DIR`: consents, account IDs, watches (with the IDs of transactions that already fired), and OAuth tokens. Balances and transactions are never written to disk. Delete the folder and you forget everything. Back it up if you don't want to re-consent.

There's even a local Ollama path — point a local model at the same tools over stdio, and no AI vendor ever sees a transaction. The README is refreshingly honest about the catch: an 8B model "is not yet trustworthy with money." Correct per-account balances, a wrong total, ten minutes per answer. A 30B-class model on a real GPU is where it starts to get useful.

## The Self-Hosting Setup

You need a free Enable Banking account and about ten minutes. Here's the Docker path for the server case.

```bash
docker run -d --name bankmcp --restart unless-stopped \
  -p 8080:8080 -v bankmcp-data:/data ghcr.io/noskillish/bankmcp:latest
```

Or with compose:

```yaml
services:
  bankmcp:
    image: ghcr.io/noskillish/bankmcp:latest
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - bankmcp-data:/data
```

Then put a TLS terminator in front. Caddy needs exactly two lines:

```
YOUR-HOST { reverse_proxy localhost:8080 }
```

Set `BASE_URL` to your public address and open it. A fresh server shows a setup page.

**The setup flow:**

1. **Register an Enable Banking application.** The setup page can do this for you — it signs in with a one-time link, creates the application with the right redirect and policy addresses, generates a key pair, and stores the ID and key. Or you do it by hand at the Enable Banking control panel and paste the application ID and `.pem` key file.
2. **Choose Production or Sandbox.** Production is for your real accounts; Sandbox is for test data. A production application for *your own* accounts gets activated once with "Activate by linking accounts."
3. **Set a password** of twelve characters or more. This is your only login.
4. **Add the connector in your assistant.** In claude.ai: *Settings → Connectors → Add custom connector →* paste `https://YOUR-HOST/mcp`, then click Connect and enter your admin password. In Claude Code: `claude mcp add --transport http bank https://YOUR-HOST/mcp`.
5. **Say "connect my bank."** It looks up your bank, gives you a link, you log in at your bank's own site and approve, and the accounts appear.

The desktop-only path is even simpler — no deployment at all:

```bash
claude mcp add bankmcp -- npx -y bankmcp
```

That's the whole thing. Ten minutes, a Docker container, and your AI can read your bank.

## What the Banker Worries About

This is the part most posts skip, and it's the part I can't skip, because I've sat on the other side of the desk.

Let me start with the thing that is genuinely, structurally fine, because I want to be fair to the project.

**Read-only is a real property, not marketing.** There are no payment tools. The worst thing the agent can *do* is read a balance and say something wrong about it. It cannot move money. That is the single most important security decision in the whole design, and it's the difference between "your AI can read your bank" and "your AI can spend your money." The second one is a nightmare; the first one is merely risky.

**Your credentials never touch the middle.** You log in at your bank's own site. Enable Banking sees the consent, not your password. That's how PSD2 is designed, and it's the part of this that's actually regulated.

But here's what I worry about, in roughly the order I worry about it:

**1. The agent can lie, and you can't always tell.** A read-only AI with a money tool is a *summary machine*, and summaries of money can be wrong in ways that matter. The project's own Ollama test is the clearest example: an 8B model returned "correct per-account balances, a wrong total." Imagine that wrong total, confidently stated, in a context where you're about to make a decision about it. The model isn't malicious — it's just not reliable with arithmetic at that size. That's a new category of financial risk that doesn't exist with a spreadsheet, because a spreadsheet doesn't have a confident-but-wrong mode.

**2. Prompt injection is now pointed at your money.** I wrote an entire post about this — [MCP Servers Are Your New Attack Surface](/blog/2026-08-16-mcp-servers-attack-surface/) — and bankmcp is a textbook case. If an agent is reading a transaction description or a bank's web content that contains a malicious instruction, the "no MCP output is safe" problem now has a financial dimension. bankmcp has some real defenses here: notifications go to exactly one `NOTIFY_WEBHOOK_URL` that the operator sets on the host, and a watch cannot name its own webhook, so a talked-into assistant can't exfiltrate transaction data to an attacker's address. That's genuinely good design. But it doesn't make the *conversation* safe — an agent that can read your balance can be socially engineered into *reporting* that balance somewhere it shouldn't.

**3. The consent is the actual key.** This is the thing non-bankers miss. Your bank's open-banking consent is not a login — it's a standing permission that lasts up to 180 days. bankmcp tells you when one is about to expire, and the same conversation renews it. But the consent is the crown jewel, and it lives in a single JSON file on your server. Back it up if you care about not re-consenting; delete it to forget everything. If someone compromises that file, they don't have your password — they have something that is, in some ways, better. Revoking the consents at your bank is the real kill switch, one step beyond deleting the state file.

**4. The admin password is the whole kingdom.** There is one user. Anyone with the admin password can read your accounts. The project is blunt about this: "Use a long one." And if you forget it, you set `ADMIN_PASSWORD` on the host and restart. This is fine for a single self-hoster — it's exactly how your Vaultwarden or Actual Budget server works. But it means the security posture of your *entire financial-read access* collapses down to: *one password, one JSON file, one container.* For a lot of people, that's actually a regression from "my bank's app with biometric auth and their fraud team."

**5. The "one hop you don't control" is doing real work.** Enable Banking is licensed, regulated, and this is how PSD2 is *supposed* to work. But I'd be lying if I said the chain-of-trust doesn't keep me up slightly. Every balance and transaction you ask for passes through their servers on the way to yours. They say they don't store it and don't see your credentials, and I believe the design. But from a banker's chair, "a third party I've never met sits between me and my bank account" is a sentence I'm trained to flinch at, even when the third party is legitimately licensed.

## So Should You Run It?

Here's where the two people in my head actually agree, and it's the part that might surprise you:

**Yes — read-only, self-hosted, for your own accounts, with eyes open. This is the good version of this idea.**

Because here's the thing the banker in me also knows: the alternative isn't "no AI touches my money." The alternative is that *someone else's* AI touches your money, and you get a marketing page instead of a threat model. Plaid has been aggregating your transactions for years. Your bank's own app is already running models on your spending. The question was never *whether* software reads your bank account — it's *whose software, with whose incentives, and can you see what it does.*

bankmcp answers that question the way I'd want it answered: open source, self-hosted, read-only, no payments, no telemetry, no hosted service, explicit threat model in the README, and a kill switch that's just "delete a folder or revoke a consent." That is genuinely the most honest version of "AI reads my bank" that currently exists, and it's the one I'd point someone toward if they were going to do this anyway.

The caveats are real, and I've written them above, but they're not reasons to run away — they're reasons to run it *carefully*:

- Run it for your own accounts, not anyone else's. Enable Banking's restricted mode is explicitly for individual non-commercial use, and the project doesn't change those terms.
- Use a long admin password, and set the `NOTIFY_WEBHOOK_URL` so you get an alert on every sign-in.
- Don't trust a small local model with money. Use a capable model if you're doing local, or accept that a cloud model is doing the reading.
- Treat the consent as the crown jewel. Back it up, and know that revoking it at your bank is the real kill switch.
- And remember the read-only promise cuts both ways: it can't spend your money, but it also can't *fix* your money. It reads. You decide.

## The Bottom Line

bankmcp is the moment where my finance cluster and my MCP cluster on this site finally meet, and I've been waiting for it. A read-only, self-hosted MCP server for your bank is exactly the kind of thing this site exists to cover — and it's also exactly the kind of thing that needs a banker's caution wrapped around the install instructions.

Your bank account is the one dataset where "wrong" and "catastrophic" overlap. So wire AI into it the way you'd wire anything else valuable into your homelab: deliberately, read-only, on your own hardware, with a threat model you actually read — and with the part of your brain that knows what a disputed transaction looks like switched firmly on.

---

*Want the rest of the stack this fits into? See my guide to [building your first MCP server](/blog/2026-07-21-mcp-for-homelab-build-first-server/), the [MCP attack surface](/blog/2026-08-16-mcp-servers-attack-surface/) post on why no MCP output is safe, and the [self-hosted budgeting comparison](/blog/2026-09-11-self-hosted-budgeting-actual-budget-firefly-iii-ynab/) for the Actual Budget vs Firefly III breakdown that pairs naturally with a read-only bank connector.*
