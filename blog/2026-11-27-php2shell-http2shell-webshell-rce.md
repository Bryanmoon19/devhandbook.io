---
layout: post.njk
title: "php2shell / http2shell: The New Web-Shell RCE Class Hitting PHP, Node & Python"
date: 2026-11-27
description: "A new family of web-shell RCE tools — php2shell, http2shell, and their cluster — is dominating GitHub trending (CVE-2026-109618/109619) and sitting on the HN front page. Homelabbers run exactly this surface: *arr apps, Nextcloud, n8n, WordPress. Here's what this class actually is, why it lands so hard on self-hosted PHP/Node/Python apps, and a hardening playbook you can run tonight."
tags: ["security", "rce", "webshell", "cve", "php", "node", "python", "homelab", "self-hosted", "sonarr", "radarr", "nextcloud", "n8n", "wordpress", "hardening", "cve-2026-109618", "cve-2026-109619"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-27-php2shell-http2shell-webshell-rce/"
affiliate: false
cta: true
---

# php2shell / http2shell: The New Web-Shell RCE Class Hitting PHP, Node & Python

If you run a homelab, there's a category of vulnerability you've learned to tune out: the *web-shell RCE*. You've seen the advisory a thousand times — "an attacker who can upload a malicious file or influence a deserialization path can achieve remote code execution." You skim it, note that it needs a specific plugin or a specific misconfiguration, and move on, because your apps are updated and your plugins are few.

**This week's trending cluster is different, and it's worth your attention precisely because it's aimed at your stack.**

A new family of tools — **php2shell**, **http2shell**, and a cluster of siblings grouped under the same umbrella — is sitting at the top of GitHub trending, tied to **CVE-2026-109618** and **CVE-2026-109619**, and the `http2shell` project is on the Hacker News front page. The through-line across all of them: they turn a *web server* into a *shell*, and they do it against the exact platforms homelabbers self-host — **PHP (WordPress, Nextcloud), Node (n8n, *arr-adjacent tooling, dashboards), and Python (the glue scripts, the bots, the automation).**

There is no self-hoster playbook for this yet. The advisory churn is already happening, and every "check your version" explainer is copy-pasting the CVSS boilerplate. This post is the other thing: **what this class actually is, why it lands so hard on your stack, and a concrete hardening playbook you can run against your own boxes tonight.**

---

## The short version: what "php2shell / http2shell" actually means

Let's be precise, because the naming is doing a lot of work and it's easy to misread.

**A web shell** is the payload — a small file or code snippet dropped onto a server that gives the attacker a command interface over HTTP. You point your browser at `http://target/shell.php?cmd=id`, and the server runs `id` and prints the result. That's the whole idea: the web server becomes your terminal.

**php2shell / http2shell** are the *tooling* around that idea — not just a static shell, but a framework that:

1. **Packages polyglot web shells** for PHP, Node, and Python targets, so one tool covers all three runtimes.
2. **Automates delivery** — the part that turns "there's a file-upload or template-injection bug" into "here's your shell." It handles the upload, the path-guessing, the `.php`→`.phar`→`.phtml` extension bypass, the `.htaccess` tricks.
3. **Provides the C2 layer** — instead of a dumb one-shot shell, it gives a persistent, interactive session with file browser, upload/download, and (in some variants) tunneling or reverse-connect behavior.

The reason it's a *cluster* and not a single tool is that the underlying vulnerability class is shared. **CVE-2026-109618** and **CVE-2026-109619** are two specific CVE IDs in the same family, and the tooling has branched into `php2shell`, `http2shell`, and several near-identical siblings as contributors add runtimes, obfuscation, and evasion. From the defender's side, the exact tool name matters less than the class: **an attacker is automating the delivery of web shells against your PHP/Node/Python apps, and the tooling is now polished enough that it's trending.**

### The two CVEs, in plain terms

- **CVE-2026-109618** — the PHP-side entry point. The details vary by report, but the class is the familiar one: an untrusted-input path (file upload, template injection, or an insecure deserialization/unserialize call) that lets an attacker place or invoke a `.php` file, then hit it over HTTP. The "2shell" tooling automates exactly this chain.
- **CVE-2026-109619** — the Node/Python-side entry point. Same idea, different runtime: a template-injection, `eval`/`exec`-style sink, or a dependency that deserializes untrusted input, letting an attacker execute server-side code.

I'm deliberately not giving you a step-by-step exploit recipe — that's not the point of this post, and the PoCs are already circulating anyway. The point is that **the tooling to exploit this class is now off-the-shelf, and it targets the runtimes you actually run.**

---

## Why your homelab is exactly the target

Here's the uncomfortable part. The platforms this cluster targets — PHP, Node, Python — are the *default* runtimes of the self-hosted web apps homelabbers love:

| App | Runtime | What it exposes |
|-----|---------|-----------------|
| **WordPress** | PHP | Plugins/themes galore, file-upload paths, XML-RPC, `unserialize` in a dozen plugins |
| **Nextcloud** | PHP | File uploads, sharing, third-party apps, a huge PHP surface |
| **n8n** | Node | Workflow definitions that execute code, webhook endpoints, community nodes |
| **Sonarr / Radarr / Lidarr** | .NET (but PHP/Node adjacent) | Web UI + API exposed on your LAN, often behind a reverse proxy |
| **The *arr ecosystem tooling** | Python / Node | Scripts, bots, indexers, downloaders — lots of glue code |
| **Grafana / dashboards** | Node / Go | Auth bypass + plugin paths |
| **Custom automation** | Python | Your own scripts, webhooks, and glue |

Three things make this worse for homelabbers specifically:

**1. You expose apps the way they weren't designed to be exposed.** `n8n` behind a Cloudflare Tunnel, `Nextcloud` on a forwarded port, WordPress on a cheap VPS — you're running *intended-for-LAN* software on the *public internet*, and the hardening defaults don't come with it.

**2. The patch cadence is slow.** *arr apps and WordPress are the two most "I'll update it next weekend" categories in homelabbing. A web-shell class that automates delivery against them punishes exactly that habit.

**3. The blast radius is your whole network.** A web shell on `n8n` isn't just "my automation box is compromised" — `n8n` holds credentials for everything else it automates. A shell on Nextcloud means your files. A shell on WordPress means your DB. And because homelabs are flat networks, one shell is usually a stepping stone to the NAS, the backup server, and the credentials vault.

This is why the "nobody targets homelabs" line doesn't hold. **You're not being targeted; you're being swept.** Automated tooling doesn't care that your box is "just a hobby server" — it cares that it's a PHP/Node/Python app with a reachable port and a known file-upload or injection path.

---

## The hardening playbook

Let's move to the part you can act on. This is ordered by impact-per-effort: do the first four tonight, and you've closed the majority of the surface this class exploits.

### 1. Inventory your PHP / Node / Python exposure

You can't harden what you can't name. List every self-hosted web app you run, its runtime, and — critically — **how it's exposed.** For each, ask:

- Is it reachable from the public internet, or only the LAN?
- Is it behind a reverse proxy, a tunnel, or a forwarded port?
- Does it accept file uploads or execute user-supplied code (workflows, templates, plugins)?

```bash
# Quick inventory of running web services and what they expose
ss -tlnp | grep -E ':(80|443|8080|8081|8443|8006|5678|9000|3000)\b' || netstat -tlnp 2>/dev/null | grep LISTEN
```

The point isn't the exact port list — it's the *map*. You want a written list of "what's running, what language, how exposed." Most homelabbers discover, when they actually write it down, that they've exposed two or three more PHP/Node apps than they remembered.

### 2. Patch the apps — and automate it, don't "remember" it

The single highest-leverage fix for this class is boring: **keep the apps current.** A web-shell RCE needs *a* bug to ride in on, and the two CVEs in this cluster both have patches (or mitigations) in current releases.

- **WordPress:** core auto-updates should be on, but plugins/themes are the real surface. Use a plugin manager that auto-updates, and *delete* unused plugins — every unmaintained plugin is a door.
- **Nextcloud:** it has a built-in updater and a security-advisory checker. Enable both, and actually read the security warnings it shows you in the admin panel.
- **n8n:** pin to a supported release, watch its security changelog (it's had a string of auth and injection fixes), and update on a schedule, not on vibes.
- ***arr apps:** they update fast and the community is loud about security releases. Subscribe to the release feed rather than checking manually.

The meta-point: **"I'll update next weekend" is the vulnerability.** Web-shell tooling trends because there's a population of unpatched apps to sweep. Don't be in it.

```bash
# Example: check for pending updates across common self-hosted apps
# (adjust paths/containers to your setup — this is illustrative, not universal)
docker ps --format '{% raw %}{{.Names}}\t{{.Image}}{% endraw %}' | sort
```

Then go read the release notes for anything that hasn't moved in 60+ days. That's your patch backlog.

### 3. Kill the file-upload and code-execution paths you don't need

The entire `2shell` family *needs an entry point* — a file upload, a template injection, a deserialization sink. You can remove a huge fraction of the attack surface by disabling the entry points you don't actually use:

- **WordPress:** disable file editing (`define('DISALLOW_FILE_EDIT', true);` in `wp-config.php`), restrict `xmlrpc.php` (or block it outright if you don't use it), and block PHP execution in `wp-content/uploads` via `.htaccess` or your reverse proxy.
- **Nextcloud:** restrict which file types can be uploaded, disable the third-party apps you don't use, and don't run the `occ` commands or expose `data/` through the web root.
- **n8n:** this is the big one. **Don't expose n8n to the public internet without auth.** If you must, put it behind an authenticating proxy. Disable the "execute command" node for non-admin users, and treat every community node as a potential injection sink.
- **Custom Python/Node scripts:** if a script doesn't need to accept untrusted input, don't let it. A webhook that runs `eval` on a query parameter is the exact thing this tooling feeds on.

```nginx
# Example nginx: block PHP execution in WordPress uploads
location ~* /wp-content/uploads/.*\.php$ {
    deny all;
}
```

```php
// wp-config.php: disable the file editor
define('DISALLOW_FILE_EDIT', true);
```

### 4. Harden your runtime configs

The web-shell class is amplified by permissive runtime defaults. A few high-value settings:

**PHP (php.ini / fpm pool):**

```ini
; Disable the dangerous functions most web shells need
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source
; Don't allow remote file includes
allow_url_include = Off
allow_url_fopen = Off
; Harden session handling
session.use_strict_mode = 1
```

> **Caveat:** `disable_functions` can break legitimate apps (WordPress and Nextcloud sometimes call `shell_exec` for maintenance tasks). Test it, and if an app needs a function, remove that one rather than disabling the whole list. The goal is to *deny the shell its tools*, not to break your apps.

**Node (for n8n and Node services):**

- Run as a non-root user inside the container or systemd unit.
- Set `NODE_ENV=production`.
- Don't pass `--inspect` or `--eval` flags in production.
- Keep `exec`/`spawn` calls out of untrusted-input paths.

**Python:**

- Run services in a venv or container as non-root.
- Never `eval`/`exec` untrusted input; prefer `ast.literal_eval` for parsing data.
- Pin dependencies and review them; a `subprocess` call on attacker-controlled input is the same bug in Python that it is in PHP.

### 5. Put a Web Application Firewall (or reverse-proxy rules) in front

A WAF is the last line, not the first, but it's genuinely useful against *automated* web-shell delivery, because the tooling sends recognizable payloads. Options that fit a homelab:

- **Cloudflare's free tier** (if you front your apps through Cloudflare) — its managed rules block a lot of web-shell and injection patterns out of the box.
- **ModSecurity / Coraza** on your reverse proxy (Traefik, Caddy, nginx) — heavier to set up, but self-hosted and tunable.
- **Fail2ban + jails** for the request patterns — it won't stop a crafted shell, but it'll slow down the *sweeping*.

The realistic framing: a WAF won't save you from a *targeted* attacker with a custom payload, but it will block the *automated* sweeps that this cluster enables — and automated sweeps are what homelabbers actually face.

### 6. Assume compromise, and build the blast-radius containment

This is the homelab-specific part the generic advisories miss. **Your goal isn't just to prevent a shell — it's to make sure a shell on one app doesn't own your network.**

- **Network segmentation.** Put internet-exposed apps on a separate VLAN/subnet from your NAS, your backups, and your password manager. A shell on `n8n` should not be able to reach your `vaultwarden`.
- **Per-service credentials.** Don't reuse a single database password or API key across apps. The shell grabs whatever the app has access to; make that "as little as possible."
- **Don't run apps as root.** Docker containers and systemd units should run as least-privilege users, with read-only filesystems where possible.
- **Separate your secrets.** A web shell can read the app's config — so don't put your *other* credentials in the app's config. Use a secrets manager or environment injection, and scope each secret to the one app that needs it.

```yaml
# Example docker-compose: least-privilege + read-only filesystem
services:
  n8n:
    image: n8nio/n8n
    user: "1000:1000"
    read_only: true
    tmpfs:
      - /home/node/.n8n
    environment:
      - NODE_ENV=production
      # auth required; no anonymous webhook execution
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASS}
    ports:
      - "127.0.0.1:5678:5678"   # bind loopback only; front via a proxy with auth
```

> **The loopback-bind trick deserves emphasis:** `127.0.0.1:5678:5678` means n8n isn't directly reachable from the network at all — you reach it *through* your reverse proxy, which is where you enforce auth, TLS, and any WAF rules. This single line removes a whole class of "exposed-by-accident" surface.

---

## What to do *right now*, in order

If you've read this far and just want the checklist:

1. **Inventory** — write down every PHP/Node/Python web app you run and how it's exposed. (10 minutes)
2. **Patch** — update WordPress (especially plugins), Nextcloud, n8n, and the *arr apps. Delete unused plugins. (30 minutes)
3. **Close entry points** — `DISALLOW_FILE_EDIT` + block PHP in uploads (WordPress), restrict uploads and disable unused apps (Nextcloud), force auth + disable command-exec nodes (n8n), block `xmlrpc.php`. (20 minutes)
4. **Harden runtimes** — `disable_functions` in PHP (tested!), non-root Node/Python, production flags. (20 minutes)
5. **Contain blast radius** — loopback-only binds, per-service credentials, network segmentation, least-privilege users. (ongoing)
6. **Add a WAF layer** — Cloudflare free rules or Coraza/ModSecurity on your proxy, if you front through one. (optional, but useful)

Do 1–4 tonight. That closes the majority of what the `php2shell`/`http2shell` cluster is built to exploit.

---

## The honest caveats

A few things to keep straight so you don't walk away with false comfort:

- **There's no single "patch" for a class.** CVE-2026-109618 and 109619 are two IDs; the underlying bug *class* (web-shell delivery via upload/injection/deserialization) is perennial. Your defense is layered habits, not a one-time update.
- **`disable_functions` is not a silver bullet.** It's a useful tripwire, but a determined attacker has bypasses (LD_PRELOAD, ImageMagick, and other vectors). It raises the bar, it doesn't end the game.
- **A WAF is not a fix.** It catches the *automated* and the *known*; a custom payload sails past it. Don't let a WAF become an excuse to skip patching.
- **Exposure is the real enemy.** The single most effective move in this entire post is the boring one: **don't put apps on the public internet unless you have to, and when you do, front them with auth.** Everything else is mitigation.

---

## The bottom line

The `php2shell` / `http2shell` cluster is trending because it's the convergence of three things homelabbers have been ignoring: the PHP/Node/Python web apps we self-host, the "patch it next weekend" cadence we keep, and the flat, trust-everything networks we build.

The tooling being off-the-shelf and on the HN front page doesn't mean you're about to be individually targeted. It means the *sweeping* is about to get easier — and sweeps hit whoever left a door open, not whoever was singled out.

Your defense is the unglamorous checklist above: **inventory, patch, close entry points, harden runtimes, contain the blast radius.** None of it is new. All of it is now *necessary*, because there's a polished, trending tool built specifically to walk through the doors you forgot to close.

Run the first four steps tonight. The web shell that trends this week will be replaced by another next week — but a homelab that's inventoried, patched, and hardened doesn't care which tool is trending.

---

*Which of these apps are you exposing, and did your inventory turn up anything you'd forgotten was public? I'd especially like to hear from n8n and WordPress self-hosters — those are the two I see people treat as "set and forget" most often. Find me on [GitHub](https://github.com/bryanmoon19) or drop a comment below.*

*If this was useful, you might also like [CVE-2026-98432: the Linux TCP use-after-free playbook](/blog/2026-11-23-cve-2026-98432-linux-tcp-use-after-free/), [MCP servers are your new attack surface](/blog/2026-08-16-mcp-servers-attack-surface/), and [Sonarr security hardening](/blog/2026-04-12-sonarr-security-hardening/).*
