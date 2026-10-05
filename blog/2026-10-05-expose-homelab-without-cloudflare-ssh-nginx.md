---
layout: post.njk
title: "Expose Your Homelab Without Cloudflare: Zero-Dependency Tunnels with SSH + Nginx"
date: 2026-10-05
description: "You don't need cloudflared, frp, rathole, or any other tunnel daemon. OpenSSH's built-in reverse forwarding plus Nginx on a $5 VPS is a complete HTTP tunnel using only software you already have installed. No new dependencies, no third party in your request path, no Cloudflare — just two tools you've been running for years."
tags: ["cloudflare", "de-cloudflare", "tunnel", "tunneling", "ssh", "nginx", "reverse-proxy", "self-hosted", "homelab", "nat", "networking", "privacy", "trust", "autossh", "systemd"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-05-expose-homelab-without-cloudflare-ssh-nginx"
affiliate: true
cta: true
---

There's a weird gap in the de-Cloudflare series, and I only noticed it because a reader pointed it out.

I wrote [the audit](/blog/2026-08-21-audit-cloudflare-dependency/), the [runbook](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/), and then [a whole comparison of self-hosted tunnel tools](/blog/2026-09-03-self-hosted-tunnel-alternatives-gopher-frp-rathole/) — Gopher, frp, rathole, boringproxy. The message was always the same: *to replace Cloudflare Tunnels, you install a new tunnel daemon.*

A reader replied: "Why would I install a tunnel tool at all? I already have SSH and Nginx running on every box I own."

And… he's right. I'd been so deep in the "which tunnel daemon" question that I'd skipped the obvious answer sitting in front of me. **OpenSSH does reverse tunnels natively.** It's been able to do this since the 1990s. Pair it with Nginx on a VPS and you have a complete HTTP tunnel — no Cloudflare, no `cloudflared`, no frp, no rathole, no *new software whatsoever*.

This post is that answer. The zero-dependency tunnel, using only the two tools you've been running for years.

## Why You've Been Overlooking This

Here's the thing about the tunnel-tool comparison I wrote last month: **every one of those tools is reimplementing a feature SSH already has.**

frp's "reverse proxy" mode? That's `ssh -R`. rathole's "connect out to a relay"? That's `ssh -R`. Gopher's "one command, no config"? That's also `ssh -R`, except SSH is already installed. The only real difference is that these tools wrap SSH's reverse forwarding in a friendlier config file and add a few extras (dashboards, auto-reconnect, HTTP-specific routing).

But if you're already running OpenSSH on your homelab boxes — and you almost certainly are — the tunnel is *already installed*. You just haven't pointed it at the problem yet.

The tradeoff is honest: SSH's reverse forwarding is a TCP tunnel, not an HTTP-aware reverse proxy. It'll happily forward raw bytes, but it won't do SNI-based virtual hosting, TLS termination, or per-host routing on its own. **That's where Nginx comes in.** Nginx is also already installed on basically every VPS and homelab box, and it's the natural complement: SSH moves the bytes, Nginx routes and terminates them.

Two tools you already have. Zero new dependencies. Full control of your request path. That's the pitch.

## The Architecture

```
Internet ──▶ Your VPS (public IP) ──▶ Nginx ──▶ SSH reverse tunnel ──▶ Your service
                │                       │                              │
                │  terminates TLS       │  routes by hostname          │  lives behind NAT
                └── listens on 80/443   └── forwards to localhost:PORT └── never opens a port
```

Three pieces:

1. **Your homelab box** runs `ssh -R` — an *outbound* connection to the VPS that maps a remote port on the VPS back to a local port on your box.
2. **Your VPS** runs Nginx, which terminates TLS and forwards traffic for `app.yourdomain.com` to `localhost:PORT` — where `PORT` is the port SSH is listening on.
3. **Your service** runs behind NAT on your homelab box, reached by the tunnel at `localhost:PORT`.

No inbound ports on your home network. No dynamic DNS. No Cloudflare. Your home IP never appears in a DNS record — the public endpoint is the VPS, which is exactly what you want.

The cost, same as every self-hosted tunnel: **you need a VPS with a public IP.** That's non-negotiable — something has to be the public endpoint. The question is whether it's Cloudflare's edge or a $5 box you control.

## Step 1: Set Up the SSH Reverse Tunnel

This is the core of it, and it's one line.

On your homelab box (the one behind NAT, running the service you want to expose):

```bash
ssh -R 8080:localhost:32400 youruser@vps.example.com
```

Let me unpack that flag, because it's the whole post in one argument:

- `-R 8080` — "on the *remote* (VPS) side, listen on port 8080"
- `localhost:32400` — "and forward anything that arrives there back to `localhost:32400` on *this* (home) box"
- `youruser@vps.example.com` — the SSH connection that carries the tunnel

So: traffic hits port 8080 on the VPS, travels back down the SSH connection, and lands on port 32400 on your home box. That's a reverse tunnel. It's called "reverse" because the direction of the tunnel is the opposite of the SSH connection — SSH connects *out*, but traffic flows *in*.

### The catch: bind address

By default, `ssh -R` binds the remote port to `localhost` only, which is actually what you want here — Nginx on the same VPS connects to `localhost:8080`, and nothing else can reach it directly. If you ever need the port bound to all interfaces, you need `GatewayPorts yes` on the VPS's sshd config. **Don't do that unless you know why** — binding to localhost only is a security feature.

### Test it

While the SSH session is open:

```bash
# On the VPS
curl http://localhost:8080
```

You should get the response from your home service. If so, the tunnel works. Kill the SSH session and the tunnel dies with it — which is why you don't run this in a terminal.

## Step 2: Make the Tunnel Survive Reboots (autossh + systemd)

A bare `ssh -R` dies when the connection drops or the box reboots. You need it to reconnect automatically. Two tools for this: `autossh` (the classic answer) and `systemd` (the modern answer). Use both.

### Install autossh

```bash
# Debian/Ubuntu
sudo apt install autossh

# macOS
brew install autossh
```

`autossh` wraps `ssh` and restarts it whenever the connection drops, with a configurable retry interval. The key flags:

- `-M 0` — disable autossh's monitoring port (you don't need it; systemd will handle restarts)
- `-o ServerAliveInterval=30 -o ServerAliveCountMissing=3` — detect dead connections fast
- `-o ExitOnForwardFailure=yes` — fail loudly if the port can't be forwarded
- `-N` — don't run a remote command (tunnel only)
- `-T` — no pseudo-terminal

### The systemd unit

Put this on your homelab box:

```ini
# /etc/systemd/system/tunnel-plex.service
[Unit]
Description=SSH reverse tunnel for Plex
After=network-online.target
Wants=network-online.target

[Service]
User=youruser
ExecStart=/usr/bin/autossh -M 0 -N -T \
    -o "ServerAliveInterval=30" \
    -o "ServerAliveCountMissing=3" \
    -o "ExitOnForwardFailure=yes" \
    -R 8080:localhost:32400 \
    youruser@vps.example.com
Restart=always
RestartSec=10
# Give the tunnel time to establish before Nginx retries
TimeoutStartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tunnel-plex.service
sudo systemctl status tunnel-plex.service
```

### The key part: key-based auth

A tunnel that needs a password prompt is a tunnel that dies. Set up SSH key auth so the connection is passwordless:

```bash
# On your homelab box — generate a key if you don't have one
ssh-keygen -t ed25519 -C "tunnel-plex"

# Copy it to the VPS
ssh-copy-id youruser@vps.example.com
```

Now `autossh` can reconnect silently, forever, with no human in the loop.

## Step 3: Route and Terminate with Nginx

The tunnel gets bytes to `localhost:8080` on the VPS. Now you need to tell Nginx that `app.yourdomain.com` should be served by that port.

```nginx
# /etc/nginx/sites-available/app.yourdomain.com
server {
    listen 80;
    server_name app.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (many homelab dashboards need this)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Longer timeouts for slow services
        proxy_connect_timeout 60s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

Enable it and get a TLS cert with certbot (or use Caddy if you prefer — the SSH tunnel doesn't care what terminates TLS in front of it):

```bash
sudo ln -s /etc/nginx/sites-available/app.yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# TLS with certbot
sudo certbot --nginx -d app.yourdomain.com
```

Now `https://app.yourdomain.com` terminates TLS at Nginx on your VPS and routes down the SSH tunnel to your service. **The entire path is yours.** No third party sees the traffic, logs it, or can change it.

## Step 4: Multiple Services (The Pattern Scales)

One tunnel per service gets unwieldy fast. The cleaner pattern: **one SSH connection, many forwarded ports, Nginx routes by hostname.**

```bash
# On your homelab box, one autossh connection forwards several services
autossh -M 0 -N -T \
    -o "ServerAliveInterval=30" -o "ServerAliveCountMissing=3" \
    -o "ExitOnForwardFailure=yes" \
    -R 8080:localhost:32400 \   # Plex
    -R 8081:localhost:8096 \   # Jellyfin
    -R 8082:localhost:8123 \   # Home Assistant
    -R 8083:localhost:8006 \   # Proxmox
    youruser@vps.example.com
```

Each port is a separate `-R`. Then on the VPS, each Nginx `server` block points `proxy_pass` at its own `127.0.0.1:PORT`. One SSH connection, one Nginx, N services, all routed by hostname.

A cleaner alternative if you run many services: forward a single port to an internal reverse proxy (Nginx, Caddy, or Traefik) on your home box, and let *that* do the per-hostname routing locally. But that adds a moving part — for a handful of services, the many-`-R`-flags approach is simpler and easier to reason about.

### SSH config to keep it tidy

Once you have more than two `-R` flags, move the boilerplate into `~/.ssh/config`:

```sshconfig
Host vps-tunnel
    HostName vps.example.com
    User youruser
    IdentityFile ~/.ssh/tunnel_ed25519
    ServerAliveInterval 30
    ServerAliveCountMissing 3
    ExitOnForwardFailure yes
```

Then the autossh command collapses to:

```bash
autossh -M 0 -N -T \
    -R 8080:localhost:32400 \
    -R 8081:localhost:8096 \
    vps-tunnel
```

Much cleaner.

## Step 5: Harden It (Non-Negotiable)

The security model is identical to every tunnel I've written about: **your VPS is now a public-facing attack surface that routes traffic into your home network.** Don't skip this.

1. **SSH key auth only.** Disable password auth on the VPS. The tunnel user should be restricted — ideally not a sudo user at all.

```bash
# On the VPS, /etc/ssh/sshd_config
PasswordAuthentication no
PermitRootLogin no
```

2. **Restrict the tunnel user.** Give the tunnel user a shell that can't do anything except hold the connection open, or use `ForceCommand internal-sftp` / a restricted shell. At minimum, use a dedicated user with no privileges.

3. **Bind the tunnel to localhost only.** Don't set `GatewayPorts yes` unless you have a specific reason. Localhost-only means the tunnel port is only reachable from Nginx on the same box, not from the public internet directly.

4. **The tunnel is a transport, not auth.** SSH gets traffic to your service; it doesn't authenticate your users. Put real auth in front of anything you expose — basic auth in Nginx, an SSO layer like [Authelia](/blog/2026-08-08-self-hosted-auth-sso-showdown/), or at minimum a strong app password.

5. **fail2ban on the VPS.** SSH brute-force is the single most common attack you'll see the moment your VPS has a public IP.

```bash
sudo apt install fail2ban
sudo systemctl enable --now fail2ban
```

## Honest Tradeoffs

I said I'd be honest, so here it is: the SSH + Nginx tunnel is not strictly "better" than frp or rathole. It's *different*, and the difference is exactly one thing — **zero new dependencies.**

**What you gain:**

- **Nothing new to install.** OpenSSH and Nginx are already on your boxes. No new binary to trust, update, or audit.
- **No third party in the request path.** Same as any self-hosted relay, but you didn't even add a tunnel tool to your supply chain.
- **Rock solid.** SSH has been battle-tested for 25 years. `autossh` for 20. This isn't a young project that might vanish.
- **Fully understood.** No black box. `ssh -R` is a single, well-documented flag, and Nginx is the most documented web server on earth.

**What you give up (vs. frp/rathole/Gopher):**

- **No dashboard.** You manage tunnels via systemd units and Nginx configs. Some people like the frp web UI; you don't get that here.
- **Raw TCP only.** SSH reverse forwarding moves TCP bytes. No built-in UDP, no HTTP-aware routing, no per-hostname magic — that's all Nginx's job, in front.
- **More moving parts to wire yourself.** frp gives you auto-reconnect and config files out of the box. Here you assemble autossh + systemd + Nginx yourself. It's not hard, but it's *more pieces*.
- **No built-in auth backends.** frp has token/OIDC auth built in; here you lean on SSH keys (for the tunnel) and whatever you put in front of the service (for the users).

**My honest take:** if you're already running SSH and Nginx — and you are — this is the tunnel to reach for *first*. It's not the flashiest, but it's the one with the smallest footprint and the least new trust. Reach for rathole if you need raw speed, frp if you need a dashboard, Gopher if you want a drop-in Cloudflare replacement. But for "expose my homelab without Cloudflare and without installing anything," SSH + Nginx wins by a mile.

## When NOT to Use This

- **High-throughput media streaming.** SSH's encryption adds CPU overhead, and a single SSH connection is a single TCP stream (head-of-line blocking). For heavy media, rathole or a direct WireGuard link will be faster. (Though for *occasional* Plex web-UI access, SSH + Nginx is fine.)
- **You need UDP.** SSH reverse forwarding is TCP-only. Game servers, QUIC, and other UDP services need something else.
- **You have dozens of services and want a management UI.** The systemd-unit-per-service model works, but a dashboard is nicer at scale.

## The Bottom Line

The de-Cloudflare series was always about one thing: **replacing a third party in your request path with something you own.** The audit found the dependencies. The runbook gave the migration steps. The tunnel comparison offered replacement daemons.

But the quiet truth hiding in all of it is this: **you probably already own the replacement.** OpenSSH's `-R` flag has been a reverse tunnel for 25 years, and Nginx has been the reverse proxy in front of it for almost as long. Pair them with `autossh` and a systemd unit, and you have a complete HTTP tunnel with exactly zero new dependencies.

No `cloudflared`. No frp. No rathole. No new supply chain to trust. Just `ssh -R 8080:localhost:32400 youruser@vps.example.com` and an Nginx `proxy_pass`.

That's the whole post, really. The rest is just making it survive a reboot.

---

*This is the fourth post in the de-Cloudflare series, and the one that closes the tunnel question. Read the [audit](/blog/2026-08-21-audit-cloudflare-dependency/) for the inventory, the [runbook](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/) for the migration, and the [tunnel-tool comparison](/blog/2026-09-03-self-hosted-tunnel-alternatives-gopher-frp-rathole/) for the daemon-based alternatives this post complements.*

**Related Reading:**
- [Cloudflare Tunnel Alternatives: The Self-Hosted Tunnel Stack (Gopher, frp, rathole, boringproxy)](/blog/2026-09-03-self-hosted-tunnel-alternatives-gopher-frp-rathole/)
- [De-Cloudflare: The Self-Hosted Trust Runbook (Audit, Migrate, Verify)](/blog/2026-08-22-audit-and-de-cloudflare-self-hosted-trust/)
- [The Cloudflare Trust Audit: How to Find Every Silent Dependency and Move Off It](/blog/2026-08-21-audit-cloudflare-dependency/)
- [Cloudflare Tunnels: Expose Your Homelab Without Opening a Single Port](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/)
- [Headscale: Self-Host Your Own Tailscale Control Plane](/blog/2026-08-24-headscale-self-host-tailscale/)
