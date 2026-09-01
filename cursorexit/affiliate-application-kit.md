# Affiliate Application Kit — Ready to Submit (Aug 31, 2026)

> **Why this matters:** These 3 programs are the gate that turns CursorExit + the blog into income. Every result card and tool CTA already has a `PLACEHOLDER_*_REF` waiting for the approved ref. Each application is ~5 min with this kit. Do them in this order (biggest traffic driver first).

---

## 1. Cloudflare Affiliate — HIGHEST PRIORITY

**Apply:** https://www.cloudflare.com/partners/ (Partner / Affiliate signup)

**Copy-paste application:**

- **Name:** Bryan Moon
- **Business email:** *(use your real one — dmn4lif3@gmail.com or a devhandbook.io address if you have one)*
- **Website:** https://devhandbook.io
- **What you do:** I run devhandbook.io, a developer-tools + self-hosting blog and interactive tool site. I write in-depth guides on Cloudflare Workers, Pages, and tunnels (e.g. "Cloudflare Tunnels for Homelab", "Audit & De-Cloudflare Your Self-Hosted Stack", "Cloudflare Workers Free Tier"), and I build free interactive dev tools (JSON formatter, JWT debugger, base64 converter, AI model picker) hosted on Cloudflare Pages.
- **Traffic:** *(paste your GA4 monthly sessions — check the weekly analytics cron or GA dashboard)*
- **Audience:** Self-hosters, homelab enthusiasts, indie devs — high-intent buyers who deploy on Cloudflare.

**After approval:** Replace `PLACEHOLDER_CLOUDFLARE_REF` in `_data/affiliates.json` + the 3 tool-page CTAs (json-formatter, jwt-debugger, base64-converter) + CursorExit result cards.

---

## 2. Hetzner Affiliate

**Apply:** https://www.hetzner.com/affiliate-program/ (or partner portal)

**Copy-paste application:**

- **Name:** Bryan Moon
- **Account:** *(your Hetzner account — create one if you don't have it)*
- **Website:** https://devhandbook.io
- **What you do:** devhandbook.io — self-hosting and homelab guides. I recommend Hetzner VPS/cloud in multiple posts: self-hosted email that delivers to Gmail, WireGuard VPN setup, local-LLM homelab hardware, and my new CursorExit tool (which recommends self-hosting AI coding tools on your own box).
- **Traffic:** *(paste GA4 monthly sessions)*
- **Audience:** Self-hosters actively deploying VPS — the exact people who buy Hetzner cloud.

**After approval:** Replace `PLACEHOLDER_HETZNER_REF` in `_data/affiliates.json` + email post inline link + tool CTAs + CursorExit result cards.

---

## 3. OVHcloud Affiliate

**Apply:** https://www.ovhcloud.com/en/affiliate-program/ (or partner portal)

**Copy-paste application:**

- **Name:** Bryan Moon
- **Account:** *(your OVH account — create one if needed)*
- **Website:** https://devhandbook.io
- **What you do:** devhandbook.io — self-hosting and homelab guides. I recommend OVHcloud VPS as a backup hosting option in my self-hosted email and VPN guides, and in my CursorExit tool for self-hosted AI coding.
- **Traffic:** *(paste GA4 monthly sessions)*
- **Audience:** Self-hosters and homelab users comparing VPS providers.

**After approval:** Replace `PLACEHOLDER_OVH_REF` in `_data/affiliates.json` + email post inline link + tool CTAs + CursorExit result cards.

---

## Where the placeholders live (search for `PLACEHOLDER_`)

```bash
cd ~/Projects/devhandbook.io && grep -rn "PLACEHOLDER_" --include="*.njk" --include="*.json" --include="*.html" --include="*.md" . | grep -v node_modules | grep -v _site
```

- `_data/affiliates.json` — central config (Cloudflare, Hetzner, OVH refs)
- `_includes/cta.njk` — blog post CTA card
- `json-formatter/index.html`, `jwt-debugger/index.html`, `base64-converter/index.html` — tool page sponsor slots
- `blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail.md` — inline Hetzner/OVH links
- `cursorexit/index.html` — result card affiliate slots (currently `affiliate: false` on all tools; flip to true + add ref once approved)

## Amazon (already live)
- Tag `devhandbook26-20` — working in 2 posts. No action needed.

---

## The one thing I need from you

I can't submit these — they're web forms tied to your email/account login. **You need to:**
1. Open each Apply link
2. Paste the kit above
3. Submit

That's ~15 min total. Once you get the approval emails, send me the ref codes and I'll wire all the placeholders + flip the CursorExit affiliate flags in one pass.
