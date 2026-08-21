# Affiliate Program Application Checklist (for Bryan)

These 3 programs are the gate that unlocks the rest of the affiliate strategy. Each takes ~15-30 min. Do them in this order (biggest traffic driver first).

## 1. Cloudflare Affiliate — HIGHEST PRIORITY
- **Why:** Your biggest traffic driver is the Cloudflare Workers/Pages posts. Cloudflare has a Partner Program with recurring revenue share.
- **Apply:** https://www.cloudflare.com/partners/ (or the affiliate/partner signup)
- **What you need:** Business email, website (devhandbook.io), traffic stats.
- **After approval:** Replace `PLACEHOLDER_CLOUDFLARE_REF` in `_data/affiliates.json` + the 3 tool-page CTAs.

## 2. Hetzner Affiliate
- **Why:** Email + homelab hosting posts naturally recommend Hetzner VPS/cloud. Solid recurring commissions.
- **Apply:** https://www.hetzner.com/affiliate-program/ (or via partner portal)
- **What you need:** Account, website, traffic.
- **After approval:** Replace `PLACEHOLDER_HETZNER_REF` in `_data/affiliates.json` + email post inline link + tool CTAs.

## 3. OVHcloud Affiliate
- **Why:** Backup hosting option for the same posts. Good for VPS recommendations.
- **Apply:** https://www.ovhcloud.com/en/affiliate-program/ (or partner portal)
- **What you need:** Account, website, traffic.
- **After approval:** Replace `PLACEHOLDER_OVH_REF` in `_data/affiliates.json` + email post inline link + tool CTAs.

## Where the placeholders live (search for `PLACEHOLDER_`)
- `_data/affiliates.json` — central config (Cloudflare, Hetzner, OVH refs)
- `_includes/cta.njk` — blog post CTA card
- `json-formatter/index.html`, `jwt-debugger/index.html`, `base64-converter/index.html` — tool page sponsor slots
- `blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail.md` — inline Hetzner/OVH links

## Quick find command
```bash
cd ~/Projects/devhandbook.io && grep -rn "PLACEHOLDER_" --include="*.njk" --include="*.json" --include="*.html" --include="*.md" .
```

## Amazon (already live)
- Tag `devhandbook26-20` — already working in 2 posts. No action needed.
