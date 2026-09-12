---
layout: post.njk
title: "Self-Hosted Invoicing in 2026: Invoice Ninja vs Crater vs Akaunting"
date: 2026-09-12
description: "FreshBooks is $30/month and QuickBooks keeps raising prices. Here's the honest head-to-head of the three serious self-hosted invoicing apps — Invoice Ninja, Crater, and Akaunting — scored for recurring billing, payment gateways, and client portal quality, plus a working Docker Compose stack for the winner."
tags: ["invoice-ninja", "crater", "akaunting", "self-hosted", "invoicing", "freelancing", "small-business", "homelab", "docker", "comparison", "accounting"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-09-12-self-hosted-invoicing-invoice-ninja-crater-akaunting/"
affiliate: true
cta: true
---

If you freelance, invoice, or run a side business, you already know the pain: FreshBooks is $30/month, QuickBooks keeps raising prices, and every "free" invoicing tool is either capped at a handful of clients or quietly monetizing your client list. The self-hosted crowd has three serious answers, and they're all open source: **Invoice Ninja**, **Crater**, and **Akaunting**.

The problem is that "self-hosted invoicing" is deceptively hard. It's not enough to generate a PDF — the *recurring billing* has to actually fire, the *payment gateway* has to actually take money, and the *client portal* has to not look like it was built in 2009. Get any one of those wrong and you're back to emailing PDFs and chasing payments by hand.

I work in finance for a living, and I've run all three on my Proxmox homelab. Here's the honest breakdown, scored for the freelancer who wants to get paid without a subscription.

## The One Question That Matters

Before the comparison, let's name the real pain point, because it's the thing every generic listicle skips:

> **Which one actually gets you paid — recurring invoices that fire on schedule, a payment gateway that takes the money, and a client portal your customers don't hate?**

That's the whole game. An invoicing app that just makes pretty PDFs is a template, not a tool. The value is in the automation: the invoice that sends itself, the reminder that chases the late payer, the "pay now" button that turns a PDF into cash. Everything below is scored against that question.

## The Three Contenders

**Invoice Ninja** — the freelancer's workhorse. Recurring invoices, auto-billing, payment gateways (Stripe, PayPal, and 40+ more), a client portal, quotes, time tracking, and expense tracking. The "I want FreshBooks but I want to own it" choice.

**Crater** — the minimalist. Clean, modern UI, invoices and estimates, a simple client portal, and not much else. The "I just need to send invoices and get paid" choice.

**Akaunting** — the full accounting suite. Invoices, bills, banking, double-entry bookkeeping, and a paid app marketplace for add-ons. The "I want QuickBooks but self-hosted" choice.

## The Scored Comparison

| | Invoice Ninja | Crater | Akaunting |
|---|---|---|---|
| **Recurring invoices** | Yes (auto-bill) | No | Yes (limited) |
| **Payment gateways** | 40+ (Stripe, PayPal, etc.) | Stripe, PayPal, Razorpay | Stripe, PayPal (via apps) |
| **Client portal** | Excellent (view + pay) | Good (view + pay) | Fair |
| **Quotes / estimates** | Yes | Yes | Yes |
| **Time tracking** | Yes (built-in) | No | No (via app) |
| **Double-entry accounting** | No (cash-basis) | No | Yes |
| **Self-host difficulty** | Moderate (needs MySQL) | Moderate (needs MySQL) | Moderate (needs MySQL) |
| **Cost** | Free (self-host) | Free | Free (core) |
| **Learning curve** | Low | Very low | High |

## The Winner: Invoice Ninja

For most freelancers and small businesses, **Invoice Ninja** is the answer. It's the closest thing to a drop-in FreshBooks replacement — recurring invoices that auto-bill, a genuinely good client portal where customers can view and pay invoices, time tracking, and a payment-gateway list that covers basically every country. The self-hosted version is the full product, not a crippled "community edition."

Here's a working Docker Compose stack (Invoice Ninja v5 needs MySQL — it's a two-container setup, not a single image):

```yaml
services:
  invoiceninja:
    image: invoiceninja/invoiceninja:5
    restart: unless-stopped
    ports:
      - "8080:80"
    environment:
      APP_URL: https://invoice.yourdomain.com
      APP_KEY: base64:CHANGE_ME_32_CHAR_RANDOM_STRING
      APP_DEBUG: "false"
      DB_HOST: db
      DB_DATABASE: ninja
      DB_USERNAME: ninja
      DB_PASSWORD: change-me-strong-password
    depends_on:
      - db
    volumes:
      - ./ninja-public:/var/www/app/public
      - ./ninja-storage:/var/www/app/storage

  db:
    image: mysql:8
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: ninja
      MYSQL_USER: ninja
      MYSQL_PASSWORD: change-me-strong-password
      MYSQL_ROOT_PASSWORD: change-me-root-password
    volumes:
      - ./ninja-db:/var/lib/mysql
```

On first launch, open `https://invoice.yourdomain.com`, run the setup wizard, and connect your payment gateway. Then point your clients at the portal URL.

### The gotchas (the part tutorials skip)

1. **Email deliverability is the silent killer.** Invoice Ninja sends invoices, reminders, and payment receipts by email — and if you use a plain SMTP relay, half of them land in spam. Use a transactional email provider (Postmark, SES, or Mailgun) or at minimum a properly configured SMTP with SPF/DKIM. A client who never sees the invoice is a client who never pays it.

2. **The payment gateway is where the money actually happens.** Invoice Ninja supports 40+ gateways, but you still need to sign up for Stripe or PayPal and paste in the API keys. The self-hosted app is free; the gateway takes its normal ~2.9% + $0.30 per transaction. That's the one cost you can't self-host away.

3. **HTTPS is non-negotiable for the client portal.** Your clients will type their card details into your portal. A reverse proxy (Caddy, Nginx, Traefik) with a Let's Encrypt cert is mandatory — not optional. A client portal served over plain HTTP is a liability, not a feature.

4. **Back up the database, not just the files.** Invoice Ninja's data lives in MySQL, not the mounted volumes. A nightly `mysqldump` (or a restic snapshot of the `ninja-db` volume) is your entire disaster-recovery plan. This is your revenue history — don't skip it.

## When to Pick Crater Instead

**Pick Crater** if you want the absolute simplest thing that still looks professional. It's invoices, estimates, a clean client portal, and Stripe/PayPal/Razorpay — and nothing else. No time tracking, no recurring billing, no accounting. It's the choice for the freelancer who sends a handful of invoices a month and wants zero learning curve.

The tradeoff is real: Crater's simplicity means no auto-billing and no recurring invoices. If you bill the same client monthly, you're re-creating that invoice by hand every time. That's fine at five invoices a month and miserable at fifty.

## When to Pick Akaunting Instead

**Pick Akaunting** if you want *actual accounting*, not just invoicing. It's double-entry bookkeeping, bills, banking, and a real chart of accounts — the closest self-hosted thing to QuickBooks. The catch is that a lot of the power (bank feeds, some payment gateways, payroll) lives in a paid app marketplace, and the learning curve is steep. It's a bookkeeping system that happens to send invoices, not an invoicing tool.

## What You Give Up vs. FreshBooks / QuickBooks

Let me be honest about the tradeoffs, because this is where self-hosted invoicing either sticks or fails:

- **You lose the "it just works" bank reconciliation.** QuickBooks' automatic bank feeds are genuinely good. Self-hosted means manual reconciliation or a paid bridge. Budget for a few minutes a week of bookkeeping.
- **You lose the hand-holding.** FreshBooks has support, onboarding, and a mobile app that's actually polished. Invoice Ninja's mobile app is fine but not great; Crater and Akaunting are web-first.
- **You gain ownership.** Your client list, your invoice history, your revenue data — on your server, not a SaaS that can raise prices or sunset features.
- **You gain a skill.** Running your own invoicing server is the same muscle as running Vaultwarden or Immich — and it compounds with everything else on this site.

## The Bottom Line

Self-hosted invoicing is a solved problem in 2026 — you just have to accept that the payment gateway and email deliverability are the two things you'll configure once and then stop thinking about. Most freelancers should start with **Invoice Ninja** (recurring billing, great portal, 40+ gateways). If you want dead-simple invoices, **Crater** is the choice. If you want real double-entry accounting, **Akaunting** is the serious option.

The point is the same one I keep making across this site: your invoices are your revenue history — the one dataset you'll still care about in ten years. Don't leave it on someone else's server, and don't pay $30 a month for the privilege, when running your own is this easy.

---

*Not ready to self-host yet? I built a [Small Business Finance Tracker](/finance-tracker/) — a 6-sheet Google Sheets system (income, expenses, P&L, invoices, tax estimator) that gets you clean books without a server. If you're freelancing, check the [Freelancer Tax Estimator](/freelancer-tax-estimator/) to see what you'll actually owe, and the [Freelance Rate Calculator](/freelance-rate-calculator/) to price yourself right. Want the rest of your self-hosted stack? See [self-hosted budgeting](/blog/2026-09-11-self-hosted-budgeting-actual-budget-firefly-iii-ynab/), [Vaultwarden for passwords](/blog/2026-04-19-vaultwarden-self-hosted-password-manager/), and [self-hosted notes](/blog/2026-09-09-self-hosted-notes-joplin-notesnook-memos-standard-notes/).*
