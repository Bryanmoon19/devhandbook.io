---
layout: post.njk
title: "Automate Your Own Internal Certificates with Step-CA + ACME"
date: 2026-10-23
description: "Every internal cert you buy is rent paid to a CA that doesn't know your network and can revoke trust with a press release. Step-CA gives you a self-hosted internal PKI that issues real certificates via ACME — the same protocol Let's Encrypt uses — so your services, mTLS, and dev boxes stop depending on anyone else's trust. Here's the full walkthrough."
tags: ["step-ca", "acme", "pki", "tls", "certificates", "mtls", "self-hosted", "homelab", "lets-encrypt", "cloudflare", "de-risk", "security", "internal-ca", "openssl"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-23-step-ca-internal-certificates"
affiliate: false
cta: true
---

# Automate Your Own Internal Certificates with Step-CA + ACME

Here's a small confession: for years, I paid money for a problem that shouldn't have been a problem.

Every internal service I ran — a Homarr dashboard, a Proxmox node, a Grafana instance, a dev box, a staging API — needed a TLS certificate. And for years, the default move was the same one everyone makes: buy a wildcard cert, or throw everything behind a reverse proxy and let someone else handle the certs for me.

Let me be precise about what that actually was. I wasn't buying *security*. TLS for an internal network doesn't need a publicly trusted CA — my machines trust each other, and nothing inside my LAN is trying to convince a stranger's browser that `grafana.lan` is legit. What I was actually doing was **renting trust from a consolidating handful of companies**, handing them a monthly or yearly fee, and — in the case of the reverse-proxy-everything approach — routing my own internal traffic through a third party whose job it is to sit in the middle of connections.

That's the part nobody says out loud. The CA market has spent two decades consolidating into a few giant roots. Cloudflare and friends have made "we'll terminate your TLS for you" so convenient that a whole generation of self-hosters has quietly given up on owning their own certificates. And every one of those moves de-risks *their* business while quietly re-risking *yours*.

This post is the fix. **Step-CA** is a self-hosted certificate authority that speaks **ACME** — the exact same protocol Let's Encrypt uses — so any ACME client (certbot, Caddy, Traefik, `step`, even a container sidecar) can get real, short-lived, automatically-renewing certificates from *your* CA, not someone else's. No public CA. No wildcard subscription. No Cloudflare in the middle of your internal traffic.

Here's the full walkthrough, copy-paste included.

## The Problem, Stated Precisely

Before I show you the fix, let me name the three ways self-hosters currently get certificates, and why each one quietly gives up control:

**1. Buy a wildcard cert from a public CA.** This works, but it's a subscription for a thing your internal network doesn't need. A public CA's entire value is that *every browser on earth* trusts its root. Your internal `*.lan` domains don't need that. You're paying for global trust to secure a basement. Worse, a wildcard cert is one secret that, if leaked, lets an attacker impersonate *every* host behind it.

**2. Route everything through Cloudflare (or a similar proxy) and let it terminate TLS.** This is the de-risking-in-reverse move. You get "free" certificates in exchange for putting a third party directly in the path of your traffic. They decrypt, inspect, and re-encrypt. The moment you do this for *internal* traffic, you've built a backhaul through someone else's infrastructure for no good reason.

**3. Self-signed certs with OpenSSL.** Free and self-hosted, but miserable to manage: no automation, no revocation, no rotation, and every client throws a trust error you have to manually silence. It's the "works but hurts forever" option.

**Step-CA** is the fourth option, and it's the one that's been missing from the self-hosting stack for too long: a real internal CA with a real protocol (ACME), real automation, real revocation, and real short-lived certificates — running on your own box, trusting only what you tell it to trust.

## What Step-CA Actually Is

Smallstep's Step-CA is a certificate authority you run yourself. The important part isn't that it's "a CA" — OpenSSL has been able to act as a CA for decades. The important part is that it speaks **ACME v2**, the protocol that made Let's Encrypt blow up, plus Smallstep's own `step` CLI protocol.

Why ACME matters: it means you don't have to write custom enrollment scripts for every service. There's already a mature ecosystem of ACME clients that do the "prove you control this hostname, get a cert, renew it automatically" dance for you. By speaking ACME, Step-CA inherits all of that for free. Your Traefik, your Caddy, your certbot cron job — they don't care whether the CA behind the protocol is Let's Encrypt or your basement box. They just do the dance.

The other thing Step-CA gives you that self-signed certs never will: **short-lived certificates with automatic renewal.** Instead of buying a 2-year cert and forgetting about it until it expires at 3 AM on a Saturday, Step-CA issues certs with a default lifetime you set (I use 24 hours for internal services), and ACME clients renew them silently before they expire. If a key leaks, the blast radius is a day, not two years.

## Setting It Up

I run Step-CA in Docker on my Proxmox host. Here's the full stack. If you've followed any of my other [self-hosting guides](/blog/2026-06-17-immich-photo-management-homelab/), this fits right in.

### Step 0: The Plan

Before you run anything, decide on two things:

1. **Your CA's name and root identity.** This is baked into the root certificate, so pick something you won't hate in five years. I use `Internal Root CA`.
2. **Your ACME provisioner name.** This is the credential your clients authenticate against. I use `internal`.

### Step 1: Initialize the CA

The cleanest way is to run `step ca init` once to generate the root key, intermediate key, and config, then bind those files into the container. Here's the init:

```bash
docker run --rm -it \
  -v step-ca:/home/step \
  smallstep/step-ca \
  step ca init \
    --name "Internal Root CA" \
    --dns "ca.lan" \
    --address ":443" \
    --provisioner "internal" \
    --password-file /home/step/password.txt
```

You'll be prompted for a few things, and it'll write the CA artifacts (`certs/`, `secrets/`, `config/`) into the `step-ca` volume. The `--password-file` flag is there so the root key is encrypted with a password you control — keep that password somewhere safe (a password manager, not the compose file).

### Step 2: Docker Compose

Here's the compose file that keeps the CA running and backed up:

```yaml
services:
  step-ca:
    image: smallstep/step-ca:latest
    container_name: step-ca
    restart: unless-stopped
    ports:
      - "9000:9000"
    environment:
      - STEPPATH=/home/step
      - DOCKER_STEPCA_INIT_NAME=Internal Root CA
      - DOCKER_STEPCA_INIT_DNS_NAMES=ca.lan
      - DOCKER_STEPCA_INIT_PROVISIONER_NAME=internal
      - DOCKER_STEPCA_INIT_PASSWORD_FILE=/home/step/secrets/password
    volumes:
      - step-ca:/home/step
```

Note: I run the ACME/HTTPS listener on a non-privileged port (`:9000`) and let the reverse proxy handle 443 — but for a pure internal CA there's no reverse proxy in the path at all. Clients hit `https://ca.lan:9000/acme/acme/directory` directly. (Yes, the double `/acme/acme/` is correct — Step-CA's ACME directory endpoint genuinely has that path.)

### Step 3: Distribute the Root CA to Your Machines

This is the one manual step, and it's the whole point: **you decide what trusts your CA.** Install the root certificate onto each device that should trust your internal certs:

```bash
# On Debian/Ubuntu/Pi OS (Linux):
sudo cp certs/root_ca.crt /usr/local/share/ca-certificates/internal-root-ca.crt
sudo update-ca-certificates

# On macOS:
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain certs/root_ca.crt
```

Now your machines trust certs issued by *your* CA, and only your CA. No browser on the public internet trusts it — which is exactly right, because nothing on the public internet should be hitting these hosts.

### Step 4: Add an ACME Provisioner

If you initialized with a provisioner named `internal`, you're mostly set. But to make ACME enrollment smooth, you'll want a provisioner that lets clients prove identity via a pre-shared password or an ACME challenge. The simplest for a homelab is **HTTP-01** (port 80 challenge) or **DNS-01** if you control a DNS server internally:

```bash
step ca provisioner add acme \
  --type ACME \
  --x509-default-dur 24h \
  --x509-max-dur 720h
```

This adds an ACME provisioner with a 24-hour default cert lifetime and a 30-day maximum.

## Enrolling Your First Client

Now the payoff. Let's say you want a certificate for `grafana.lan`. With the `step` CLI, it's one command:

```bash
step ca certificate grafana.lan grafana.crt grafana.key \
  --provisioner internal \
  --ca-url https://ca.lan:9000
```

But the more interesting path is a *real ACME client*, because that's what proves the protocol works with everything else. Here's certbot doing it:

```bash
certbot certonly --standalone \
  --server https://ca.lan:9000/acme/acme/directory \
  -d grafana.lan \
  --register-unsafely-without-email \
  --agree-tos
```

And here's the bigger idea: **Caddy and Traefik just work.** Point them at your CA's ACME endpoint and they'll request and auto-renew certs for every internal service they front — no manual steps, no expiring wildcard, no Cloudflare.

```caddy
# Caddyfile
{
    acme_ca https://ca.lan:9000/acme/acme/directory
}

grafana.lan {
    reverse_proxy localhost:3000
}
```

That's it. Caddy fetches a cert from *your* CA, renews it automatically, and you own the whole trust chain.

## The mTLS Bonus

This is where internal PKI goes from "nice" to "why doesn't everyone do this." Once you have a CA, you can issue *client* certificates and require **mutual TLS** — both sides prove who they are.

mTLS is the correct answer to a problem that self-hosters usually solve badly: how do I let my internal services talk to each other securely *without* exposing them to the internet or leaning on API keys floating around in config files?

With Step-CA, every service gets an identity certificate, and every connection requires the peer to present a valid cert signed by your CA. An attacker who gets onto your LAN can't just hit your PostgreSQL or your internal API — they need a client cert, and the CA will only issue one to an identity you've approved.

```bash
# Issue a client certificate for a service identity
step ca certificate postgres-client postgres.crt postgres.key \
  --provisioner internal \
  --ca-url https://ca.lan:9000
```

This is the "stop renting trust" idea taken to its logical end. You're not just self-hosting your certificates anymore — you're running your *own identity infrastructure*, the same way you run your own DNS, [auth](/blog/2026-08-28-self-hosted-bookmark-manager-showdown/), and [storage](/blog/2026-08-30-self-hosted-file-sync-nextcloud-seafile-syncthing/).

## What This Replaces (and De-Risks)

Let me be concrete about what I removed from my stack after setting this up:

- **The wildcard cert subscription.** Gone. One less recurring bill, one less giant shared secret.
- **Cloudflare-terminated internal traffic.** Gone. My internal services now encrypt end-to-end on my own LAN, through my own CA, with no third party decrypting in the middle. The de-Cloudflare theme is real: TLS termination is a *choice*, not a *default*.
- **The 2-year expiry panic.** Gone. Certs are 24 hours now, renewed automatically. A cert expiring is a non-event because it's constantly being replaced.
- **The "self-signed means click through the scary warning" workflow.** Gone. Your machines trust your root, so your internal certs look *valid* — because they are.

## The Honest Tradeoffs

I'll tell you what's hard, because the marketing pages won't.

**You now have a root key to protect.** This is the single biggest responsibility you take on. The root CA key is the master key to your entire internal trust. If it leaks, someone can mint certs for any of your hosts. Mitigations: encrypt it with a strong password (done during init), store it off-box, and consider an offline root + online intermediate split if you're paranoid. For a homelab, an encrypted root key on a volume you back up is a reasonable middle ground.

**Root distribution is manual and ongoing.** Every new device needs the root cert installed before it trusts your CA. There are automation tools for this (MDM, config management, a small bootstrap script), but at first it's a manual `scp` + one command per machine. Budget for it.

**You're now running infrastructure that matters.** The CA is like your DNS server — when it's down, cert *renewals* stall (though existing certs keep working until they expire). Give it `restart: unless-stopped`, back up the volume, and treat it with the same care you'd treat your router.

## The Bottom Line

The phrase I keep coming back to is this: **stop renting trust from people who can revoke it.**

Every time you pay a public CA for an internal cert, or route internal traffic through a third-party proxy "for the free certs," you're making a small bet that the consolidating handful of trust providers will keep behaving. Step-CA lets you stop making that bet. It's not hard to set up — it's a Docker container and a few commands. The hard part was never the tooling; it was realizing you were allowed to own this in the first place.

If you're already running a homelab, you have the hardware and the knowledge. Spin up Step-CA this weekend, issue your first cert, and feel the specific satisfaction of watching `certbot` hand you a certificate that *you* signed, on *your* authority, for *your* network. Trust, it turns out, is something you can self-host too.
