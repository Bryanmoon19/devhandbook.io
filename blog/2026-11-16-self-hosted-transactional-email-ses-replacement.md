---
layout: post.njk
title: "Self-Hosted Transactional Email: The SES / Resend Replacement That Actually Lands"
date: 2026-11-16
description: "Your Vaultwarden password resets are going to spam — or vanishing entirely — because SES and Resend are one misconfigured DNS record away from failure. Here's how to self-host outbound app email (resets, alerts, marketing) with nitromta, aliasflare, and mailroom, and get SPF/DKIM/DMARC right so it actually lands."
tags: ["self-hosted", "email", "transactional", "smtp", "ses", "resend", "nitromta", "aliasflare", "mailroom", "spf", "dkim", "dmarc", "deliverability", "vaultwarden", "homelab"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-16-self-hosted-transactional-email-ses-replacement"
affiliate: true
cta: true
---

There's a specific moment that converts a casual self-hoster into an email deliverability obsessive, and it usually happens in the dark. You're locked out of something. You click "forgot password." You wait. Nothing arrives. You check spam. Nothing. You wait a day, try again, and finally the reset email lands — six hours late, buried in the Promotions tab, looking like it was sent through a tin can.

That moment is almost always a **transactional email** problem, and it's a completely different animal from the inbox-email problem I wrote about in [my self-hosted email stack guide](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail). That post was about *receiving* — your inbox, your IMAP, your domain's mail flowing *in*. This one is about *sending* — the password resets, security alerts, cron-job notifications, and marketing blasts that your apps push *out*.

And here's the uncomfortable truth the tutorials skip: **the "just use SES/Resend, it's $1" advice is a trap.** Not because those services are bad — they're excellent — but because they quietly assume *you* already understand SPF, DKIM, and DMARC well enough to not break them. The moment you add a second sending service, a subdomain, or a marketing platform alongside your transactional mail, you've created a deliverability minefield. And when your Vaultwarden reset email goes to spam at 2 AM, you don't get a support ticket — you get a locked-out user.

The good news: there's now a whole generation of tools built specifically to self-host *outbound* email the right way. This is the guide I wish I had before I burned an afternoon debugging a DMARC alignment failure. Here's the full picture — the tools, the DNS, and the exact config that makes your app mail actually land.

## Why Transactional Email Is a Different Problem Than Inbox Email

First, let me draw the line clearly, because conflating the two is where most of the confusion comes from.

**Inbox email (receiving)** is about *your* mail server accepting mail for *your* domain. It's MX records, IMAP, spam filtering on the way in. The goal is "I can read mail sent to me@mydomain.com." This is what Mox, Stalwart, WildDuck, and Maddy do, and it's what my previous post covered.

**Transactional email (sending)** is about *your apps* pushing mail *out* — to *your own users*. A password reset from Vaultwarden. A "disk is full" alert from your monitoring stack. A "new login detected" notice from your SSO. A weekly newsletter from your marketing tool. The goal is "the mail my software generates actually reaches my users' inboxes."

The difference matters because the failure modes are opposite:

- **Inbox email fails when you can't *receive*.** You misconfigure a mail server, or your IP gets blocklisted, and mail to you bounces.
- **Transactional email fails when you can't *be trusted*.** Your app sends from a domain with bad SPF, a missing DKIM signature, or a DMARC policy that contradicts itself — and Gmail silently drops it, or buries it in spam, or (worst) *you* look like a phisher sending from a spoofed domain.

The tools are different too. You don't run a full IMAP server to send a password reset — you run an **SMTP relay** with a strong grasp of deliverability, or you run a **mailroom** that manages the whole outbound pipeline. That's where nitromta, aliasflare, and mailroom come in.

## The Three Tools, Explained

Let me introduce the field. These are the tools that have made self-hosted *outbound* email genuinely viable in 2026, and they each solve a different slice of the problem.

### nitromta — the self-hosted SMTP relay that speaks deliverability

[nitromta](https://github.com/nitromta/nitromta) is the closest thing to a "run this and your app mail gets delivered" answer. It's a self-hosted SMTP server designed specifically for *outbound* mail — think of it as your own private SES. Your apps (Vaultwarden, your scripts, your marketing tool) point their SMTP config at nitromta, and nitromta handles the hard part: DKIM signing, queueing, retries, bounce handling, and (crucially) the DNS discipline that keeps you off blocklists.

What makes it different from a general mail server is that it's **purpose-built for sending, not receiving**. It doesn't try to be an IMAP server or a webmail client. It's a relay that assumes the thing on the other end is an *application*, not a human, and it optimizes for that: high throughput, clean bounce tracking, webhook notifications for delivery events, and per-sender configuration so you can run a separate sending identity for "security alerts" vs. "marketing blasts."

**Best for:** the core of your outbound pipeline — the thing your apps actually talk to.

### aliasflare — the subdomain-and-identity manager for deliverability

[aliasflare](https://github.com/aliasflare/aliasflare) solves a problem you don't know you have until it bites you: **you shouldn't send transactional mail and marketing mail from the same domain.** If your password resets and your "weekly digest" both send from `@yourdomain.com`, a single spam complaint about the newsletter tanks the reputation of your *password resets*. Gmail doesn't distinguish "transactional" from "promotional" — it sees one sending domain with one reputation.

Aliasflare is a tool for managing **multiple sending identities and subdomains** on a single domain. It lets you carve out `mail.yourdomain.com` for transactional, `news.yourdomain.com` for marketing, and generate the correct SPF/DKIM/DMARC records for each — so a problem with one identity never poisons the others. It's the "separation of concerns" layer for outbound email.

**Best for:** running multiple sending identities cleanly, so your transactional mail is firewalled from your marketing mail.

### mailroom — the full outbound pipeline with a dashboard

[mailroom](https://github.com/mailroomhq/mailroom) is the "I want to see what my email is actually doing" answer. It's an open-source outbound email *platform* — think Mailgun's dashboard, but self-hosted. It gives you the whole pipeline: SMTP ingestion, DKIM/DMARC/SPF handling, a queue, retry logic, bounce and complaint webhooks, and a web UI that shows you delivery rates, bounce reasons, and open/click data.

Where nitromta is the relay and aliasflare is the identity manager, mailroom is the *control tower* — the layer that turns "I sent an email" into "I know it was delivered, opened, and clicked, and here's the graph." If you're doing any volume at all, or you care about *seeing* deliverability instead of just hoping, this is the piece that makes it visible.

**Best for:** people who want observability and analytics on top of the relay, or who are running real volume.

The beautiful part is that **these three compose.** nitromta is the relay your apps talk to, aliasflare manages the identities and DNS, and mailroom (or nitromta's own webhooks) gives you the visibility. You don't have to run all three — a minimal setup might be just nitromta — but together they cover the whole problem space that SES and Resend occupy.

## The DNS That Actually Makes It Land (SPF, DKIM, DMARC, Done Right)

Here's the part that separates "I sent an email" from "the email was delivered." The tools make this *easier*, but you still have to understand what you're asking them to do. This is the section I burned an afternoon on, so let me save you that afternoon.

### SPF — who is allowed to send as you

SPF (Sender Policy Framework) is a `TXT` record on your domain that lists the IP addresses allowed to send mail *from* your domain. When Gmail receives mail claiming to be from `you@yourdomain.com`, it looks up your SPF record and checks whether the sending IP is on the list.

```text
v=spf1 include:_spf.yourdomain.com ~all
```

The critical mistake people make here is the `~all` vs `-all` vs `+all` ending. `+all` means "anyone can send as me" — that's a spoofing invitation, never use it. `~all` (softfail) means "not on the list? mark it as suspicious but deliver." `-all` (hardfail) means "not on the list? reject it." For transactional mail where every sending IP is known and controlled, `-all` is correct — you know exactly which IPs should be sending, and anything else is spoofed.

The second mistake is **failing to include every service that sends as you.** If your marketing tool sends from its own IPs, those IPs have to be in the SPF record *too*. Miss one, and mail from that service softfails or hardfails — which is exactly the "my reset email went to spam" scenario, because Vaultwarden is sending from an IP that isn't in your SPF record.

### DKIM — the cryptographic signature that proves it's really you

DKIM (DomainKeys Identified Mail) is where most self-hosters get lost, because it involves *cryptography*. The idea is simple: your mail server signs each outbound email with a private key, and publishes the matching public key in a DNS `TXT` record. When Gmail receives your mail, it fetches the public key and verifies the signature — proving the mail wasn't tampered with and really came from you.

```text
selector._domainkey.yourdomain.com  TXT  "v=DKIM1; k=rsa; p=MIIBIjANBgkq..."
```

The two things that go wrong here:

1. **The selector mismatch.** The DKIM record lives at `<selector>._domainkey.yourdomain.com`, and the selector is a name *you* choose (or your tool generates). Your sending tool has to sign with the *same selector* whose public key is in DNS. If nitromta signs with selector `mail` but you published the key under selector `default`, the signature fails and Gmail treats the mail as unsigned.

2. **Key rotation without updating DNS.** When you rotate your DKIM key (which you should, periodically), you have to publish the new public key before the old one expires. Rotate the private key on the server but forget to update DNS, and every email you send fails DKIM until you fix it.

The good news: nitromta, mailroom, and aliasflare all *generate* the DKIM keys for you and tell you exactly which `TXT` record to paste. The bad news: you still have to paste it, and verify it resolves. That last step — *verify it resolves* — is the one everyone skips and everyone regrets.

### DMARC — the policy that ties it together (and the one that bites)

DMARC (Domain-based Message Authentication, Reporting, and Conformance) is the record that tells receivers what to do *when SPF and DKIM disagree*. It also — and this is where people get hurt — tells receivers what to do when *either* fails.

```text
_dmarc.yourdomain.com  TXT  "v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.com; ruf=mailto:forensic@yourdomain.com"
```

The `p=` policy is the landmine. It has three values:

- `p=none` — don't do anything special with failing mail (useful while you're testing, but pointless long-term).
- `p=quarantine` — put failing mail in spam.
- `p=reject` — reject failing mail outright.

Here's the trap: **people set `p=reject` before they've actually confirmed SPF and DKIM are aligned.** Then something breaks — a tool sends mail that fails DKIM because of a selector mismatch, or a new marketing service isn't in the SPF record — and *every email from your domain gets rejected.* Not marked as spam. Rejected. Your Vaultwarden resets, your alerts, your newsletter — all silently refused, and you don't even get a bounce because DMARC rejection happens at the *receiving* server.

The correct sequence is:

1. Start with `p=none`, and use the `rua=` reporting address to *actually read* the DMARC reports. They tell you exactly which emails are failing and why.
2. Fix every SPF/DKIM alignment issue the reports surface. This is the part nobody does and it's the whole game.
3. Only after your reports show clean alignment for a week or two, move to `p=quarantine`, then eventually `p=reject`.

DMARC reports (`rua`) are the single most underrated tool in deliverability. They're XML files that tell you "email from this IP, using this DKIM selector, failed alignment at 14:32." If you're not reading them, you're flying blind. Aliasflare and mailroom both surface these reports in a human-readable form, which is a big part of their value.

### The alignment rule that makes it all work

The word that keeps coming up is **alignment**, and it's the actual heart of the whole thing. For a message to pass DMARC, *at least one* of SPF or DKIM must **align** with the `From:` domain — meaning:

- **SPF alignment:** the domain in the `Return-Path` (the envelope sender) matches the domain in the `From:` header, *and* the sending IP passes SPF for that domain.
- **DKIM alignment:** the domain in the DKIM signature (`d=`) matches the domain in the `From:` header, *and* the signature verifies.

This is why subdomains matter so much. If your app sends `From: noreply@mail.yourdomain.com` but signs DKIM with `d=yourdomain.com`, that's *not aligned* — the `d=` domain doesn't match the `From:` domain. This single mismatch is responsible for more "why is my transactional mail in spam" posts than everything else combined.

The fix is to make your sending subdomain's DKIM and SPF *align* with the subdomain itself — which is exactly what aliasflare manages for you. When you carve out `mail.yourdomain.com` as a transactional identity, it generates the SPF and DKIM records *for that subdomain*, so `From: noreply@mail.yourdomain.com` aligns perfectly.

## A Working Setup: Vaultwarden Resets That Actually Land

Let me make this concrete with the exact scenario from the title: you self-host Vaultwarden (the Bitwarden-compatible password manager), and you want its password-reset and account-recovery emails to actually reach your users. Here's the fast path.

### Step 1: Carve out a dedicated subdomain

Don't send Vaultwarden's mail from your root domain. Give it its own identity:

```text
mail.yourdomain.com   (transactional — resets, alerts, account notices)
```

This is the aliasflare part. If you also send a newsletter, give *that* a separate subdomain (`news.yourdomain.com`) so marketing complaints never touch your reset emails.

### Step 2: Point Vaultwarden at your relay

Vaultwarden's admin panel has an SMTP section. Point it at nitromta (or mailroom, if you want the dashboard):

```text
SMTP Host:     smtp.yourdomain.com (or your nitromta IP)
SMTP Port:     587 (STARTTLS) or 465 (SSL)
SMTP Username: vaultwarden@mail.yourdomain.com
SMTP Password: (your relay credential)
From Address:  noreply@mail.yourdomain.com
```

### Step 3: Configure DKIM + SPF for the subdomain

Have nitromta/aliasflare generate the DKIM key for `mail.yourdomain.com`, then publish these records:

```text
# SPF for the subdomain
mail.yourdomain.com  TXT  "v=spf1 ip4:<your-relay-ip> -all"

# DKIM (selector = whatever your tool generated, e.g. "nitromta")
nitromta._domainkey.mail.yourdomain.com  TXT  "v=DKIM1; k=rsa; p=<public-key>"

# DMARC (start with p=none, read reports, then tighten)
_dmarc.mail.yourdomain.com  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com"
```

Notice the subdomain scoping. SPF, DKIM, and DMARC all live *under* `mail.yourdomain.com`, so they align with the `From: noreply@mail.yourdomain.com` address. That's the alignment rule in action.

### Step 4: Verify, then send test mail

Before trusting it, verify every record resolves and aligns. Send a test reset from Vaultwarden to a Gmail account, a Microsoft account, and a Yahoo account you control. Check where it lands — inbox, spam, or nowhere. Then check the message headers in Gmail ("Show original") and confirm you see `spf=pass`, `dkim=pass`, and `dmarc=pass`. If all three say `pass`, your mail is aligned and will land. If any says `fail`, you've found the bug before your users did.

### Step 5: Watch the DMARC reports

This is the ongoing part. Point your `rua=` address at a real mailbox, and either read the reports manually or let aliasflare/mailroom digest them. They'll tell you if anything starts failing — a misconfigured tool, an expired DKIM key, a new IP that isn't in SPF. Deliverability is not set-and-forget; it's "set, then watch."

## The Honest Verdict: Should You Ditch SES/Resend?

I've been making the case for self-hosting, so let me be straight about when it's *not* worth it.

**Keep using SES or Resend if:**

- You send a *lot* of mail and don't want to babysit an IP reputation. These services have spent years warming up their IPs, and that's genuinely hard to replicate from scratch.
- You're not interested in the deliverability internals. SES/Resend abstract the DNS and the reputation away, and that abstraction has real value.

**Self-host if:**

- **You want your resets to not depend on a third party's reputation.** When SES pauses your account for a billing hiccup or a "compliance review," your Vaultwarden resets stop. Self-hosting means *you* control the uptime of your own critical mail.
- **You want privacy.** Transactional mail often contains sensitive stuff — account activity, security alerts, reset tokens. Sending that through a third party means trusting them with it. Self-hosting keeps it on your own infrastructure.
- **You've already got the self-hosting itch.** If you run Vaultwarden, your own SSO, and a homelab full of services, transactional email is one of the last pieces you're still renting. This closes the loop.

The honest middle path — and what I'd actually recommend to most people — is **hybrid**: self-host the *critical* transactional mail (resets, security alerts, account notices) where reliability and privacy matter most, and keep the *marketing* mail on a relay or a service where deliverability-at-scale is the hard problem and the content is less sensitive anyway. The subdomain separation that aliasflare gives you makes this clean: `mail.yourdomain.com` self-hosted for the important stuff, `news.yourdomain.com` on a service for the blast.

## The Bottom Line

Self-hosted transactional email in 2026 is a solved problem *if* you understand that the hard part was never the software — it's the **DNS discipline**. SPF, DKIM, and DMARC, done right, with proper subdomain separation and alignment, is the entire game. The tools (nitromta, aliasflare, mailroom) have made the software side almost trivial; what still trips people up is the alignment rule and the DMARC policy that rejects their mail because they set `p=reject` before they verified.

The moment that started this post — the locked-out user waiting for a reset that never lands — is almost always a *DNS* problem, not a *server* problem. Somewhere in your chain, an SPF record is missing an IP, a DKIM selector doesn't match, or a DMARC policy is stricter than your actual alignment. Fix that, and your Vaultwarden resets will land every time.

My advice: if your app mail has ever gone to spam (or vanished), don't reach for a new service — reach for your DNS records. Start with `p=none`, read your DMARC reports, fix the alignment, and *then* tighten. The service you're renting is just a relay; the trust that makes mail deliverable is something you can build yourself.

---

*Are you self-hosting your outbound email? Did your password resets ever go to spam, and what was the fix? I'd love to hear what worked — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my post on [self-hosted email for receiving](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail) and [self-hosted auth and SSO](/blog/2026-08-08-self-hosted-auth-sso-showdown).*
