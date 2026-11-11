---
layout: post.njk
title: "Self-Hosted Portfolio & Investment Tracker: Track Stocks, Crypto, and Net Worth Without Mint/Personal Capital"
date: 2026-11-11
description: "Mint is dead, Personal Capital wants to upsell you a financial advisor, and every free 'net worth tracker' is monetizing your holdings. Here's the honest guide to self-hosting your own portfolio and net-worth tracker — Ghostfolio, a privacy-first crypto tracker, and the rest of the 2026 field — scored for brokerage import, crypto support, and the real-time net-worth view that actually matters."
tags: ["ghostfolio", "portfolio", "investing", "net-worth", "crypto", "self-hosted", "personal-finance", "homelab", "docker", "stocks", "money"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-11-self-hosted-portfolio-investment-tracker/"
affiliate: false
cta: true
---

Your budget answers one question: *where did my money go?* Your portfolio answers a different one entirely: *what is it worth right now?*

We've covered the first question already — [self-hosted budgeting](/blog/2026-09-11-self-hosted-budgeting-actual-budget-firefly-iii-ynab/) is a solved problem in 2026, and I made the case for running Actual Budget on your own box. But budgeting is only half the picture. The other half — your investments, your holdings, your total net worth — is still wildly underserved by the self-hosted world. Everyone knows Ghostfolio, and then the conversation awkwardly stops, as if one project were the entire category.

It's not. And the reason this gap matters is bigger than "I want a free Mint clone." Mint is dead. Personal Capital exists to funnel you into their advisory service and sits there eyeballing your brokerage balances so it can call you with a pitch. Every "free" net-worth app is monetizing the single most valuable dataset you own: not your spending, but your *wealth*.

I work in finance for a living, and I've run Ghostfolio and a handful of its competitors on my Proxmox homelab. Here's the honest decision guide for tracking stocks, crypto, and total net worth on hardware you control — no brokerage logins living in someone else's cloud, no advisory upsell, no data mining.

## Why Budgeting Tools Can't Do This (And Why It Matters)

The reason self-hosted budgeting and self-hosted portfolio tracking are two *different* problems is subtle and worth naming, because it's exactly why the tools don't overlap:

- **Budgeting is a ledger problem.** Transactions in, categories assigned, envelopes balanced. It's double-entry bookkeeping, which Firefly III and Actual Budget do beautifully.
- **Portfolio tracking is a *valuation* problem.** You own assets — stocks, funds, crypto, cash, maybe a house — and their prices move every second. The hard part isn't recording what you bought; it's keeping a *live* answer to "what is all of this worth right now, in my currency, net of fees and taxes?"

A budgeting app can tell you that you spent $500 on groceries. It cannot tell you that your portfolio crossed a rebalancing threshold this morning, or that your total net worth just ticked past a milestone because a single stock position moved. Those are different queries against different data, and they deserve different tools.

That's the real argument for a dedicated portfolio tracker, and it's the thing most generic "self-hosted finance" listicles miss: they lump budgeting and net-worth into one bullet point and call it done. They're not the same, and conflating them is how you end up manually re-keying your brokerage statement into a spreadsheet every month and quietly giving up.

## The Anchor Tool: Ghostfolio

**[Ghostfolio](https://github.com/ghostfolio/ghostfolio)** is the default answer, and it deserves the reputation. It's a web-based wealth tracker that does the valuation problem properly: you log your holdings (manually or via import), and it shows you a live net-worth dashboard with allocation charts, performance over time, and a clean breakdown across accounts and asset classes.

What Ghostfolio gets right:
- **Real-time pricing** across stocks, ETFs, funds, and crypto, pulled from public data sources so you don't hand-enter prices.
- **Multi-account support** — brokerage, retirement, crypto wallets, cash accounts, all rolled into one net-worth number.
- **Import from brokerage exports** — most brokers will hand you a CSV or an activity export, and Ghostfolio ingests it rather than demanding a live login.
- **A genuinely good UI** — it looks like the paid apps you're trying to replace, which matters because you'll be staring at it every morning.
- **Actively maintained** with a real community and regular releases, which matters when you're depending on it to wake up and show you your money.

The tradeoff is the same one that defines this whole category: **Ghostfolio does not log into your brokerage for you.** No serious self-hosted tracker does, and that's a *feature*, not a bug — more on that in a minute. You either import a CSV from your broker or add transactions manually. Set your expectations there before you start.

Here's a working Docker Compose stack:

```yaml
services:
  ghostfolio:
    image: ghostfolio/ghostfolio:latest
    restart: unless-stopped
    ports:
      - "3333:3333"
    environment:
      DATABASE_URL: postgresql://ghostfolio:CHANGE_ME@postgres:5432/ghostfolio
      REDIS_HOST: redis
      REDIS_PORT: 6379
      JWT_SECRET_KEY: CHANGE_ME_TO_A_LONG_RANDOM_STRING
      ACCESS_TOKEN_SALT: CHANGE_ME_TO_A_LONG_RANDOM_STRING
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ghostfolio
      POSTGRES_USER: ghostfolio
      POSTGRES_PASSWORD: CHANGE_ME
    volumes:
      - ./postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    restart: unless-stopped
```

Three containers — app, Postgres, Redis. On first launch, create your account (the first registered user becomes the admin), then start adding accounts and holdings. Put it behind a reverse proxy with HTTPS before you expose it; your net worth is not a dataset you want sitting on plain HTTP.

### The gotchas (the part tutorials skip)

1. **There is no live brokerage login, and that's the point.** Ghostfolio and its peers deliberately do *not* use Plaid-style account linking. You import activity exports. This is the single biggest reason people bounce off self-hosted portfolio tracking — they expect "connect my Vanguard account" and get "upload a CSV." Understand *why*: a live login means handing your brokerage credentials to a third party, which is precisely the thing you're self-hosting to avoid. Read-only *pricing* is live; read-only *balances* come from your broker's own export.

2. **Crypto is supported but not the focus.** Ghostfolio tracks crypto as an asset class, but if crypto is a large chunk of your holdings, it's not the sharpest tool — which is exactly where the next project comes in.

3. **Back up the database.** Your entire portfolio is a Postgres database plus the app's data volume. A nightly `pg_dump` or a restic snapshot of the Postgres volume is your entire disaster-recovery plan. Don't skip it — this is your *wealth* data.

## The Crypto-Specialist: crypto-portfolio-tracker

If Ghostfolio is the generalist, **[crypto-portfolio-tracker](https://github.com/lowbetweentrim/crypto-portfolio-tracker)** (around 280 stars) is the specialist. It's a privacy-first, self-hosted crypto portfolio tracker built specifically for the person who wants real-time P&L on their coins without handing their wallet data to CoinMarketCap or a SaaS tax-prep company.

What makes it worth knowing about:
- **Privacy-first by design.** Your holdings, your wallet addresses, your cost basis — all on your box, none of it shipped to a third party.
- **CSV import** from exchanges and wallets, same philosophy as Ghostfolio but tuned for crypto's quirks (airdrops, staking rewards, transfers between wallets).
- **Real-time P&L** — live pricing and unrealized gain/loss on your positions, which is the metric crypto traders actually live and die by.
- **Lightweight** — a single self-hosted service rather than a sprawling stack, so it's an easy add alongside Ghostfolio rather than a replacement.

The honest read: at ~280 stars it's young, so expect a thinner community and fewer integrations than Ghostfolio's ecosystem. But if crypto is a meaningful slice of your net worth, running it *alongside* Ghostfolio — Ghostfolio for the total picture, crypto-portfolio-tracker for the real-time coin-level P&L — is a genuinely sensible split that no single tool handles well.

## The Rest of the 2026 Field

Ghostfolio is the anchor and crypto-portfolio-tracker is the specialist, but the category is broader than those two. A quick survey of what else is out there, and where each one fits:

- **Portfolio Performance** — a desktop (not web) tracker popular in the European personal-finance community. Very deep reporting, but it's a local application, not a self-hosted server, so it doesn't give you the "check it from any device" experience the other tools do.
- **Maybe Finance / self-hosted "net worth" spreadsheets** — plenty of people run a Google Sheet with a `GOOGLEFINANCE()` call and call it a day. It works until you want crypto pricing, multi-currency, or historical tracking, at which point you've quietly rebuilt a worse Ghostfolio.
- **Firefly III's "assets" features** — if you already run Firefly III for budgeting, it can track asset *accounts* and even fetch some prices. But it's a ledger bolted onto a valuation problem; it'll show you a balance, not a portfolio with allocation and performance. Fine as a rough total, not a real tracker.

The takeaway: if you want a live, pretty, multi-asset net-worth view you'll actually open every morning, Ghostfolio is still the one to beat. The others fill niches — desktop-only reporting, spreadsheet minimalism, budget-first tracking — rather than replace it.

## The Stack I'd Actually Run

Putting it together, here's the stack I'd recommend for most people, and the reasoning behind each piece:

1. **Ghostfolio** — the backbone. Total net worth, allocation, performance across all accounts. Your single "how am I doing?" number.
2. **crypto-portfolio-tracker** — the crypto layer, if crypto is more than ~10% of your holdings. Real-time P&L at the coin level, privacy-first.
3. **Actual Budget (or Firefly III)** — the budgeting half, already covered [here](/blog/2026-09-11-self-hosted-budgeting-actual-budget-firefly-iii-ynab/). Budgeting tells you where money *went*; the trackers tell you what it's *worth*.
4. **A reverse proxy (Caddy or Nginx)** — HTTPS in front of all of it, because none of this is a dataset you expose on plain HTTP.
5. **A backup job** — restic or rsync on the Postgres/SQLite volumes, nightly. This is your wealth; treat the backups like it.

That's the complete picture, and none of it requires a brokerage login living in a SaaS cloud. Your broker's export file is the only "sync" you need, and it's the only part of the flow that ever touches the internet.

## The Honest Tradeoffs

Let me be straight about what you give up, because "self-host your portfolio" is easy to romanticize and easy to abandon:

- **You lose the "it just connects" experience.** Mint and Personal Capital had live account linking. Self-hosted trackers don't, by design. You'll be importing a CSV from your broker periodically — monthly is plenty for most people, and it takes about ninety seconds once you've done it once.
- **You become your own data-entry clerk for manual holdings.** Real estate, private equity, anything without a public price — you'll update those by hand. It's a small list, and you'll do it a few times a year.
- **You gain a *real* answer, not an upsell.** No advisory phone calls, no "we noticed your balance" emails, no data broker buying your holdings. Just your numbers on your hardware.
- **You gain the one view that matters.** Budgeting answers "where did my money go"; a portfolio tracker answers "what is it worth now." That second question is the one you'll actually ask yourself on a random Tuesday, and having it answered in real time, on your own box, is quietly the whole point.

The one thing I'd warn against is trying to make *one* tool do everything. Budgeting and portfolio tracking are different problems, and the tools reflect it. Run Actual Budget for the first and Ghostfolio for the second, and let each be good at its job instead of asking either to be mediocre at both.

## The Bottom Line

Self-hosted budgeting is a solved problem, and now self-hosted *investing* is too — it's just been hiding behind a single over-recommended name. **Ghostfolio** is the generalist worth running for the total net-worth view; **crypto-portfolio-tracker** is the privacy-first specialist if coins are a real slice of your wealth; and neither of them needs your brokerage password.

The point is the same one I keep making across this site: your net worth is the one number you'll still care about in twenty years. Don't hand it to a company that wants to upsell you an advisor or sell your holdings to a data broker — and don't pay a subscription for the privilege — when running your own is this easy.

Budgeting answers *where did my money go.* Investing answers *what is it worth now.* Own both answers.

---

*Want the budgeting half of the equation? Read [Self-Hosted Budgeting in 2026: Actual Budget vs Firefly III vs YNAB](/blog/2026-09-11-self-hosted-budgeting-actual-budget-firefly-iii-ynab/). And if you're running money-related services, make sure they sit behind a real reverse proxy — see [Expose Your Homelab Without Cloudflare](/blog/2026-10-05-expose-homelab-without-cloudflare-ssh-nginx/) and the [self-hosted auth/SSO guide](/blog/2026-08-08-self-hosted-auth-sso-showdown/) for the hardening layer.*

---

*Links: [Ghostfolio](https://github.com/ghostfolio/ghostfolio) · [crypto-portfolio-tracker](https://github.com/lowbetweentrim/crypto-portfolio-tracker) · [Portfolio Performance](https://www.portfolio-performance.info/) · [Actual Budget](https://actualbudget.org) · [Firefly III](https://www.firefly-iii.org)*
