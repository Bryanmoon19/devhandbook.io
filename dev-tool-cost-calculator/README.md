# Dev Tool Cost Calculator

A beautiful, interactive single-page tool for comparing SaaS subscriptions vs self-hosting alternatives for popular developer tools.

## What It Does

- **Real-time TCO comparison** — Enter your hourly rate, team size, and pick a tool. See instant cost breakdowns.
- **Visual bar charts** — CSS-only animated charts showing SaaS vs self-host costs.
- **Break-even analysis** — At what team size does self-hosting win?
- **Scenario analysis** — Compare costs across different team sizes at a glance.
- **Decision recommendation** — Green/yellow/red badge with plain-English advice.
- **Copy-to-clipboard** — Share results in one click.

## Built For

[devhandbook.io](https://devhandbook.io) — a resource for developers who want to make informed infrastructure decisions.

## Included Presets

| Tool | SaaS | Self-Host Alternative |
|------|------|----------------------|
| GitHub Copilot | $19/mo | Continue.dev + Ollama |
| n8n Cloud | $24/mo | Self-hosted n8n |
| Zapier | $20/mo | Self-hosted n8n / ActivePieces |
| Figma | $15/mo | Penpot |
| Notion | $10/mo | Outline / AppFlowy |
| Linear | $12/mo | Plane |
| GitHub Actions | ~$0.008/min | Gitea Actions / Jenkins |
| Cloudflare Workers | $5/mo + usage | Self-hosted Deno / Node.js |
| Datadog | $15/mo | Uptime Kuma + Grafana |
| Vercel | $20/mo | Coolify / Dokploy |
| Slack | $8.75/mo | Mattermost / Zulip |
| Sentry | $26/mo | Self-hosted Sentry |

## Usage

Open `index.html` in any modern browser. No server required — it's a single self-contained file with zero external dependencies.

```bash
open index.html
```

## Design

- Dark theme with Apple-like clean aesthetics
- Responsive layout (mobile-friendly)
- CSS-only bar charts (no charting libraries)
- Smooth animated transitions
- devhandbook.io header/nav pattern

## Tech

- Pure HTML/CSS/JavaScript
- Zero external dependencies
- Single file, fully self-contained
