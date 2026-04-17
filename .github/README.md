# devhandbook.io Deployment

## Auto-Deploy Workflow

This repository uses GitHub Actions to automatically deploy to Cloudflare Pages on every push to the `main` branch.

### How It Works

1. **Push to `main`** → GitHub Actions triggers automatically
2. **Build** → Eleventy generates the static site
3. **Deploy** → Wrangler uploads to Cloudflare Pages
4. **Live** → Site is updated in ~30 seconds

### Manual Deploy

If you need to trigger a deploy manually (e.g., after editing `_site` directly):

```bash
cd ~/Projects/devhandbook.io
npx eleventy && npx wrangler pages deploy _site --project-name=devhandbook-io
```

### Environment Variables

The following secrets must be set in your GitHub repository:

| Variable | Description |
|----------|-------------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token with Pages deployment permissions |

### Deployment URL

After deployment, your site will be live at: `https://devhandbook.io`

### Troubleshooting

**Deployment fails?**

1. Check GitHub Actions logs in `Actions` tab
2. Verify `CLOUDFLARE_API_TOKEN` is set in repository secrets
3. Ensure Node.js 20+ is available
4. Run `npm ci` to ensure dependencies are installed

**Eleventy build errors?**

- Check that all `.njk` and `.md` files are valid
- Verify `_config.json` exists and is valid
- Look for syntax errors in templates

**Wrangler deploy errors?**

- Verify Cloudflare API token has `pages:deploy` scope
- Check that `_site` directory exists and contains build output
- Ensure `wrangler.toml` is configured correctly

---

*Automated deployment enabled by Moon's Night Shift — April 17, 2026*
