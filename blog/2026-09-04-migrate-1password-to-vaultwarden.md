---
layout: post.njk
title: "Migrating from 1Password to Vaultwarden: The Complete 2026 Walkthrough"
date: 2026-09-04
description: "You already run Vaultwarden — now leave 1Password for good. The exact export/import path (1PUX vs CSV), the gotchas nobody warns you about (TOTP secrets, attachments, shared vaults), and a verification checklist so you don't lock yourself out."
tags: ["vaultwarden", "bitwarden", "1password", "password-manager", "migration", "self-hosted", "homelab", "security", "privacy", "own-your-stack"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-09-04-migrate-1password-to-vaultwarden"
affiliate: true
cta: true
---

You've been meaning to do this for months. You read the [Vaultwarden guide](/blog/vaultwarden-self-hosted-password-manager/), you spun up the container, you even logged in once — and then you went back to 1Password, because the thought of moving 400 logins by hand is exactly the kind of chore that never makes it to the top of the list.

This is the post that removes the excuse. Here's the exact path from 1Password to Vaultwarden, including the gotchas that generic "1Password alternatives" listicles never mention — the ones that will bite you *after* you've cancelled your subscription and can't go back.

I run Vaultwarden in production. I've done this migration. Here's what actually happens.

## Why Leave 1Password?

Let's be honest about the motivation, because it determines how careful you need to be.

1Password is a genuinely good product. The reason to leave isn't that it's broken — it's that it's a **subscription you don't control**. Every price hike, every policy change, every "we're moving to a new sync model" announcement is a reminder that your most sensitive data lives on someone else's server, under someone else's terms.

Vaultwarden is the same *kind* of product — a Bitwarden-compatible password manager — but it runs on your hardware. Your vault, your backups, your rules. The tradeoff is that you now own the operational burden (updates, backups, uptime). For a homelabber, that's not a burden, it's the point.

The migration itself is the scary part, so let's make it boring.

## Step 1: Export Your 1Password Vault

1Password gives you two export formats, and they are **not equivalent**. This is the single most important decision in the whole migration.

### Option A: 1PUX (preferred)

1PUX is 1Password's newer, richer export format. It's a `.1pux` file that preserves **everything** — including fields that CSV silently drops.

**How to export 1PUX:**
1. Open 1Password → **Settings** → **Export** (or **File → Export** depending on version)
2. Choose **1Password Unencrypted Export (.1pux)**
3. Enter your master password when prompted
4. Save the file somewhere safe — it is **unencrypted**, so treat it like a plaintext copy of your entire life

### Option B: CSV (fallback)

CSV is the older, simpler format. It's readable in any spreadsheet, but it **drops data**. Specifically:

- **TOTP / one-time-password secrets are lost.** Your 2FA codes live in a separate field that CSV export doesn't include.
- **Attachments are not exported at all.** Any file you attached to a login (recovery codes, key files, scans) stays behind.
- **Custom fields and sections get flattened** into a lossy approximation.

If you have *any* TOTP codes or attachments in 1Password, use 1PUX. CSV is only acceptable if your vault is pure username/password/URL and nothing else.

## Step 2: Import Into Vaultwarden

Vaultwarden is API-compatible with Bitwarden, so the import path is the same as Bitwarden's.

1. Log into your Vaultwarden web vault
2. Go to **Tools → Import Data**
3. In the format dropdown, choose **1Password 1PUX** (if you exported 1PUX) or **1Password (csv)** (if you exported CSV)
4. Select your export file
5. Click **Import**

The import is fast — a few hundred items take seconds. But don't celebrate yet. The import is where the gotchas surface.

## The Gotchas Nobody Warns You About

This is the section that separates a real migration guide from a listicle. These are the things that will bite you *after* you've deleted your 1Password account.

### 1. TOTP secrets don't survive CSV export

If you used CSV, every login that had a one-time-password code is now missing that code. Your 2FA is silently gone. You'll discover this the first time you try to log into a site and it asks for a code you no longer have.

**The fix:** Re-add TOTP secrets manually in Vaultwarden. For each affected login, open the item → **Edit** → add a **TOTP** field → paste the original secret (the `otpauth://` URI or the base32 secret). If you no longer have the secret, you'll need to disable and re-enable 2FA on that site — which is a real pain, and exactly why 1PUX is the right choice.

### 2. Attachments don't export via CSV (and 1PUX needs a separate step)

CSV drops attachments entirely. 1PUX *can* preserve them, but the import tooling for attachments is less mature — in practice, many people find attachments don't come through cleanly even with 1PUX.

**The fix:** Before you cancel 1Password, go through your vault and download every attachment to a local folder. Then re-attach them in Vaultwarden manually. It's tedious, but it's a one-time cost, and it's the only reliable way to keep your recovery codes and key files.

### 3. Shared and family vaults don't map 1:1

1Password's shared-vault model (family organizer, shared vaults, per-member permissions) doesn't translate directly to Vaultwarden's organization model. Vaultwarden uses **organizations** with **collections**, and the permission granularity is different.

**The fix:** Recreate your shared structure by hand. In Vaultwarden:
1. Create an **Organization** (Settings → Organizations)
2. Create **Collections** for each logical group (e.g. "Family", "Work", "Shared with Emma")
3. Invite members and assign them to collections
4. Move the imported items into the right collections

This is the most manual part of the migration, and there's no shortcut. Budget 20–30 minutes for a family setup.

### 4. Field-type mapping quirks

1Password's custom fields (dates, phone numbers, addresses, credit cards) don't always map cleanly to Vaultwarden's field types. You may end up with items where a "date" became a "text" field, or a credit card number landed in a generic field.

**The fix:** After import, spot-check your most-used items — especially credit cards, identities, and anything with custom fields. Fix the field types manually. It's a one-time cleanup.

## Step 3: Verify Before You Cancel

This is the step that saves you from a very bad week. **Do not cancel 1Password until you've verified the migration.**

Run this checklist:

1. **Spot-check 20 logins** — your bank, email, GitHub, and a few random ones. Confirm username, password, and URL all came through.
2. **Confirm TOTP works** — pick a login with 2FA, copy the code from Vaultwarden, and actually log in with it.
3. **Test on a second device** — install the Bitwarden app on your phone, log in against your Vaultwarden URL, and confirm sync works.
4. **Check attachments** — confirm your recovery codes and key files are present (or that you've downloaded them locally).
5. **Verify shared vaults** — have your family member log in and confirm they can see their items.

Only after all five pass should you cancel 1Password. And even then, **keep the 1PUX export file** as a cold backup for a few months.

## The Backup You Should Take Right Now

One more thing, because it's the difference between "migrated" and "migrated safely":

Vaultwarden stores everything in a SQLite database (or Postgres/MySQL if you configured it). **Back it up before and after the import.** The simplest approach:

```bash
# Stop the container, copy the data dir, restart
docker stop vaultwarden
tar -czf vaultwarden-backup-$(date +%F).tar.gz /path/to/vw-data
docker start vaultwarden
```

Or, if you want it automated, Vaultwarden has a built-in backup endpoint (`/admin` → backup) and there are plenty of cron-based backup scripts. The point is: **your vault is now your responsibility, so back it up like it matters.** Because it does.

## When to Stay on 1Password

This guide assumes you want to leave. But be honest with yourself about whether you should:

- **You don't want to run a server** → stay on 1Password. Vaultwarden's whole value proposition is self-hosting; if that's a chore, not a feature, don't do it.
- **You need guaranteed uptime** → a homelab can go down. 1Password's SLA is someone else's problem.
- **You share with non-technical family** → the migration friction is real, and a family that won't adopt the new app is a family that keeps using the old one.

For everyone else — the homelabber who already runs Vaultwarden and just needs the nudge — this is the path. It's a couple of hours of careful work, and then you never pay for a password manager again.

## Conclusion

The migration from 1Password to Vaultwarden isn't hard — it's just *fiddly*, and the fiddly parts are exactly the ones the listicles skip. Export with 1PUX (not CSV), re-add your TOTP secrets and attachments by hand, recreate your shared vaults, and **verify everything before you cancel**.

Do it once, do it carefully, and you'll have your most sensitive data on hardware you control — which is the whole point of the [own-your-stack](/blog/2026-08-21-audit-cloudflare-dependency/) philosophy this site keeps coming back to.

**Resources:**
- [Vaultwarden GitHub](https://github.com/dani-garcia/vaultwarden)
- [Bitwarden Import Guide](https://bitwarden.com/help/import-from-1password/)
- [1Password Export Documentation](https://support.1password.com/export/)

---

*Made the switch? Hit a gotcha I didn't cover? Share it in the [Discord](https://discord.gg/selfhosted) — the migration edge cases are exactly the kind of thing that saves the next person an hour.*
