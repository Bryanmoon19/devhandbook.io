---
layout: post.njk
title: "Self-Hosted Payments: The Stripe, LemonSqueezy, and Polar Alternatives for Indie Devs Who Want to Own Their Billing"
date: 2026-08-24
description: "An 'Open-source Stripe Connect alternative' hit 83 points on Hacker News this week, and indie devs are hunting for self-hostable billing. Stripe takes a cut, LemonSqueezy got acquired, and Polar is open-source but opinionated. Here's the honest breakdown of every self-hosted payments option — and how to pick the right one for your stack."
tags: ["payments", "stripe", "lemonsqueezy", "polar", "billing", "self-hosted", "indie-dev", "saas", "open-source", "merchant-of-record", "subscriptions", "developer-tools"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-24-self-hosted-payments-stripe-alternatives"
affiliate: true
cta: true
---

# Self-Hosted Payments: The Stripe, LemonSqueezy, and Polar Alternatives for Indie Devs Who Want to Own Their Billing

An **"Open-source Stripe Connect alternative"** hit **83 points** on Hacker News this week, and the thread underneath it is a familiar one: indie developers who are tired of paying a percentage of every sale to a payments middleman, and who want to *own* their billing stack the same way they own their code.

It's a real itch. Stripe takes **2.9% + 30¢** on every transaction. LemonSqueezy — the darling of the indie SaaS world — got acquired and its roadmap went quiet. Polar is open-source and genuinely good, but it's opinionated about how you should run your business. And the "just self-host it" crowd keeps pointing at a growing pile of open-source billing engines, each with a different answer to the same question: **can I run my own payments without becoming a payments company?**

I've spent the last few months writing about self-hosting everything from [email](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail/) to [auth](/blog/2026-08-08-self-hosted-auth-sso-showdown/) to [analytics](/blog/2026-08-10-self-hosted-web-analytics-2026/). Payments is the one I've been avoiding, because it's the one where "self-hosted" and "you are now legally responsible for other people's money" collide. But the HN thread made it clear the demand is real, so let's actually dig in.

This post is the honest breakdown: what "self-hosted payments" actually means, the real options, what each one costs you (in money *and* in liability), and how to pick the right one for your stack.

## First, a Crucial Distinction: What "Self-Hosted Payments" Actually Means

Before we get to the tools, we have to clear up a confusion that poisons every one of these HN threads. "Self-hosted payments" means two completely different things, and people talk past each other because they don't separate them.

### 1. Self-hosted *billing* (you still use a payment processor)

This is the sane version. You run your own subscription logic, invoicing, dunning, and customer portal — but the actual money still flows through Stripe, PayPal, or a bank. You own the *billing layer*, not the *money movement*.

This is what most people actually want. You get control over your pricing logic, your data, and your customer experience, without taking on the nightmare of PCI compliance, chargebacks, and fraud liability.

### 2. Self-hosted *payments* (you are the processor)

This is the "open-source Stripe Connect alternative" in the HN title, and it's a very different beast. You're running the thing that actually moves money — connecting to card networks, banks, or crypto rails directly. This is where you become, legally and operationally, a payments company.

The distinction matters because **the tools for #1 are mature and genuinely useful, while the tools for #2 are mostly for marketplaces and platforms that have no other choice.** If you're an indie dev selling a SaaS product, you almost certainly want #1. If you're building a marketplace where you need to split payments between sellers, you might need #2.

Let me cover both, but I'll be honest about which one you actually need.

## The Landscape: Every Real Option, Categorized

Here's the full map. I've grouped them by what they actually are, because "Stripe alternative" is a uselessly broad label.

### The Merchant of Record (MoR) — they handle tax, you pay a premium

A Merchant of Record is the company that *legally* sells your product. They collect the money, handle sales tax/VAT in every jurisdiction, deal with chargebacks, and send you a payout. You pay a higher fee (usually 5%+), but you never touch the compliance.

- **LemonSqueezy** — the indie favorite. Clean API, handles global tax, was acquired (by Stripe, ironically) and its future is now uncertain. Still works, but the "bet your business on it" confidence is gone.
- **Paddle** — the enterprise-grade MoR. More expensive, more features, more paperwork to get approved. The default for bigger indie SaaS.
- **Gumroad** — the creator-focused MoR. Great for digital products and courses, less so for SaaS subscriptions.

**When to use:** You're a solo dev or tiny team, you sell globally, and you'd rather pay 5% than spend a week a quarter on tax compliance. This is the "I just want to ship" option.

### The Payment Processor — you handle tax, they handle the card

This is Stripe's core product. You're the merchant of record, you're responsible for tax and compliance, but Stripe handles the actual card processing, PCI, and fraud.

- **Stripe** — the default. 2.9% + 30¢, best-in-class API, but you own the tax problem and the chargeback problem.
- **Braintree (PayPal)** — similar, PayPal's version, slightly different fee structure.
- **Adyen** — the enterprise processor, not really indie-friendly.

**When to use:** You have volume, you want the lowest fees, and you're willing to handle tax (or use a tax service like TaxJar/Anrok on top).

### The Open-Source Billing Engines — self-hosted #1

This is where the "self-hosted" crowd actually lives. These are the tools that let you run your own billing logic on top of a processor like Stripe.

- **Lago** — the open-source billing engine that's become the default answer. Usage-based billing, subscriptions, invoicing, dunning. Self-hostable (MIT-ish core) or hosted. This is the one most people mean when they say "self-hosted Stripe."
- **Kill Bill** — the older, battle-tested open-source billing platform. More enterprise, more Java, more powerful but heavier.
- **Chargebee / Recurly** — not open-source, but they're the hosted billing layer that sits on top of Stripe. Worth mentioning because they solve the same problem without the self-hosting.

**When to use:** You want to own your subscription logic, your data, and your customer portal, but you're fine with Stripe moving the money. This is the sweet spot for most indie devs who say "I want to self-host my billing."

### The Open-Source Payment Orchestrators — self-hosted #2

This is the "open-source Stripe Connect alternative" from the HN title. These are for marketplaces and platforms that need to route money between multiple parties.

- **Hyperswitch** — the big one. An open-source payment orchestration layer (Rust) that routes to multiple processors. Backed by real funding, genuinely impressive, but it's *orchestration*, not a processor — you still need a processor underneath.
- **Medusa** — actually a full commerce platform, but its payment architecture is modular and self-hostable, and it's often cited in these threads.
- **Solid / Moov** — not open-source, but they're the "payments as infrastructure" APIs that let you build Stripe-Connect-like flows yourself.

**When to use:** You're building a marketplace, a platform, or anything where money needs to flow *through* you to multiple sellers. This is a real need, but it's a small fraction of the people in these threads.

## The Honest Cost Comparison

Let me put numbers on this, because "Stripe takes a cut" is the complaint, and the answer is more nuanced than "self-host and pay nothing."

| Option | Fee | What you own | What you're liable for | Setup effort |
|--------|-----|--------------|------------------------|--------------|
| **LemonSqueezy / Paddle (MoR)** | ~5% + 50¢ | Nothing | Almost nothing (they're the MoR) | Low |
| **Stripe (processor)** | 2.9% + 30¢ | Billing logic, data | Tax, chargebacks, fraud | Medium |
| **Stripe + Lago (self-hosted billing)** | 2.9% + 30¢ + infra | Everything billing | Tax, chargebacks, fraud | High |
| **Hyperswitch (orchestrator)** | Varies by processor | Routing, data | Depends on processor | Very high |
| **Fully self-hosted (you're the processor)** | Card network fees (~1-2%) | Everything | *Everything* — PCI, fraud, chargebacks, tax | Extreme |

The key insight: **self-hosting your billing doesn't save you the 2.9%.** That fee goes to the card networks and the processor, and you can't avoid it by running Lago on a VPS. What self-hosting *does* save you is the *premium* — the difference between Stripe's 2.9% and a MoR's 5%, or the difference between Stripe's flat fee and a processor you negotiate with directly at volume.

For most indie devs, the honest math is: **the 2.9% isn't the problem. The 5% MoR premium is, and only if you have real volume.** If you're doing $1,000/month, the difference between 2.9% and 5% is $21. Not worth a weekend of self-hosting. If you're doing $50,000/month, it's $1,050 — and now self-hosting your billing (not your payments) starts to make sense.

## What Self-Hosting Actually Buys You (and What It Doesn't)

Let me be precise about the real benefits, because the HN thread is full of people who want to self-host for the wrong reasons.

### What it genuinely buys you

1. **Data ownership.** Your customer list, your subscription data, your revenue analytics — all in your database, not locked in Stripe's. This is the #1 real reason, and it's a good one.
2. **Pricing flexibility.** Stripe's pricing model is flexible, but it's *their* model. Lago lets you do usage-based billing, hybrid pricing, and weird custom plans that Stripe's UI fights you on.
3. **No vendor lock-in.** If Stripe bans you (it happens — usually for "high-risk" categories), you can point your billing engine at a different processor without rebuilding your whole stack.
4. **Cost at scale.** At real volume, the ability to negotiate processor rates and avoid MoR premiums adds up.

### What it doesn't buy you

1. **Lower card fees.** The 2.9% is mostly card networks + processor. You can't self-host your way out of it.
2. **Freedom from compliance.** If you're the merchant of record, you owe sales tax in every jurisdiction you sell into. Self-hosting your billing doesn't change that — it just means you're now *also* responsible for the software that tracks it.
3. **Freedom from fraud and chargebacks.** Someone has to eat the chargeback. If you're the MoR, it's you. Self-hosting doesn't make chargebacks go away; it makes them *your* problem to detect and fight.
4. **A simpler life.** Self-hosting billing is a real operational commitment. It's another service to run, monitor, back up, and secure — and this one handles money, so the stakes are higher than your [Jellyfin server](/blog/2026-08-10-jellyfin-ecosystem-stack/).

## The Decision Framework: What Should You Actually Do?

Here's the honest, opinionated answer, because "it depends" is a cop-out.

### You're a solo dev selling a SaaS, doing < $10k/month

**Use LemonSqueezy or Paddle.** The 5% MoR premium is worth it because they handle global tax, and global tax is the thing that will eat your weekends. You don't have volume, so the fee difference is trivial. Your time is better spent shipping than self-hosting billing.

The only caveat: LemonSqueezy's acquisition makes it a slightly riskier bet than it was. Paddle is the safer long-term choice if you can get approved.

### You're doing $10k–$100k/month and want to optimize

**Use Stripe + a tax service (TaxJar/Anrok), and consider Lago if you have complex pricing.** At this volume, the 2.9% vs 5% difference is real money ($2,100/month at $100k), and you can afford the tax service. Lago is worth it *if* your pricing is genuinely complex (usage-based, hybrid, custom plans). If it's simple monthly subscriptions, Stripe's native billing is fine and Lago is overkill.

### You're building a marketplace or platform

**This is the only case where the "open-source Stripe Connect alternative" is actually for you.** Look at Hyperswitch for orchestration, or Medusa if you're building a full commerce platform. But understand: you're not avoiding Stripe, you're building *on top of* processors, and you're taking on real compliance responsibility for your sellers.

### You want to be a payments company

**Don't.** Not unless you have a team, a compliance budget, and a lawyer. The "fully self-hosted processor" path is a multi-year, multi-million-dollar commitment. The open-source projects in this space are impressive, but they're building blocks for companies that have no other choice, not a weekend project for an indie dev.

## The "Payment Stack Picker" — Coming Soon

One thing I kept wishing for while writing this was a simple tool: answer a few questions (your volume, your product type, your risk tolerance, your geography) and get a recommended payment stack. The decision tree above is the manual version, but I'm building an interactive **payment stack picker** to make it one-click.

It'll live alongside the other [tools](/tools/) on this site, and it'll be free. If you want to know when it ships, the [newsletter](/blog/) is the place — or just check back here, since I'll link it from this post when it's live.

## The Bottom Line

The HN thread hit 83 points because the itch is real: indie devs are tired of paying a middleman, and "self-hosted payments" sounds like the answer. But the honest truth is that **most people in that thread don't want to self-host their payments — they want to self-host their *billing*, and those are different things.**

Here's the whole thing, compressed:

1. **Self-hosted billing ≠ self-hosted payments.** Billing is your subscription logic on top of a processor. Payments is moving the money yourself. You almost certainly want the former.
2. **You can't self-host your way out of the 2.9%.** That's card networks + processor, and it's non-negotiable. What you *can* avoid is the 5% MoR premium, and only at real volume.
3. **Lago is the real "self-hosted Stripe"** for most people — it owns your billing logic and data while Stripe still moves the money.
4. **Hyperswitch and the "Connect alternatives" are for marketplaces**, not indie SaaS. If you're not splitting payments between sellers, you don't need them.
5. **The decision is volume-driven.** Under $10k/month, use a MoR and stop thinking about it. Over $10k, Stripe + tax service. Complex pricing, add Lago. Marketplace, look at Hyperswitch.

The people who get this right stop asking "how do I self-host payments?" and start asking "what's my volume, what's my product, and how much compliance do I actually want to own?" Answer those three, and the stack picks itself.

---

*Are you self-hosting your billing, or did you decide the MoR premium is worth it? I'm genuinely curious where indie devs are landing on this in 2026 — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my pieces on [self-hosted auth](/blog/2026-08-08-self-hosted-auth-sso-showdown/), [self-hosted email](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail/), and the [self-hosted PaaS comparison](/blog/2026-08-17-self-hosted-paas-coolify-dokploy-stackdome/).*
