---
layout: post.njk
title: "Quad9 Just Exited France — Own Your DNS with a Self-Hosted Resolver"
date: 2026-10-23
description: "Quad9 pulled out of France this week over a legal order to block piracy sites, and the story hit the top of Hacker News. If your 'private DNS' depends on someone else's datacenter, you don't own your resolution. Here's why it happened, the honest decision table between Unbound, Technitium, and AdGuard Home, and a working recursive resolver you can deploy in minutes on hardware you already have."
tags: ["dns", "quad9", "unbound", "technitium", "adguard-home", "recursive-resolver", "self-hosted", "homelab", "privacy", "dnssec", "dot", "doh", "docker", "networking"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-23-self-hosted-dns-resolver/"
affiliate: false
cta: true
---

There's a story at the top of Hacker News right now, and it should bother you more than it probably does: **Quad9 is exiting France.**

The short version is that a French court ordered Quad9 to block a list of piracy-related domains at the resolver level, and Quad9 — a Swiss nonprofit whose entire pitch is "we don't block, we don't log, we answer your queries and nothing else" — decided the order was incompatible with operating there. Rather than comply, they're pulling French endpoints entirely. Swiss and international resolvers keep running; French users lose their local Quad9 presence.

I'm not going to litigate the merits of either side here. The blocking order is about piracy, and reasonable people can disagree about whether a resolver *should* be a copyright-enforcement point at all. What matters for *you*, if you run a homelab and you've spent any time thinking about DNS privacy, is the uncomfortable thing this story lays bare:

**If your "private DNS" is somebody else's IP address, you don't own your resolution. You're renting it — and the landlord can change the terms.**

Quad9, Cloudflare, Google — they're all fine, and I've recommended them myself (including in the [WireGuard + Pi-hole post](/blog/2026-04-21-wireguard-pihole-privacy-stack/)). But every one of them is a single legal order, a single policy change, or a single acquisition away from being *not your DNS* anymore. Quad9 didn't get compromised. They got a court order, and the only two options were "comply" or "leave." That's the whole menu when you depend on a third party.

This post is about the third option that never makes the headline: **run your own recursive resolver.** Talk to the root servers directly, do your own DNSSEC validation, and stop depending on anyone's upstream for the most fundamental lookup on your network. I'll cover why a recursive resolver is different from the forwarding Pi-hole you probably already run, lay out the honest decision table between the three real choices (Unbound, Technitium, AdGuard Home), and give you a working setup you can deploy tonight.

---

## The Difference Between What You Have and What You're Missing

Most people who think they've "self-hosted their DNS" have actually done something subtly different, and the Quad9 story is exactly the reason the distinction matters.

**A forwarder asks someone else for the answer.** This is what Pi-hole does out of the box, and it's how most homelabs are wired: Pi-hole receives a query, checks its blocklists, and if the domain isn't blocked, forwards the query upstream to Cloudflare or Quad9 or Google. Those upstream resolvers do the actual recursive work — they walk the DNS hierarchy, ask the root servers, ask the `.com` servers, ask the authoritative server — and hand back the finished answer. Your Pi-hole is a filter and a cache sitting on top of someone else's resolver.

**A recursive resolver does the walking itself.** Unbound, and Technitium in recursive mode, start at the root servers and resolve the entire chain themselves. When you query `example.com`, your resolver asks a root server "who runs `.com`?", asks that server "who runs `example.com`?", and asks that server "what's the IP?" It does its own DNSSEC validation against the root's keys. At no point does it send your full query to a third party.

The practical difference:

- **A forwarder leaks your query stream** to whatever upstream you picked. Cloudflare or Quad9 *sees every domain you look up* (minus whatever they claim not to log — which is a promise, not a technical property).
- **A recursive resolver leaks only fragments** — and only to the servers that genuinely need them. The root servers learn you're interested in `example.com`'s TLD; the `.com` servers learn the domain; your full query is never assembled in one place.
- **A forwarder is one court order away from vanishing.** A recursive resolver answers to the root zone and DNSSEC, full stop. Nobody can "exit" your own resolver.

None of this makes forwarders *wrong*. A forwarder is fast, easy, and gets you a cache that's been warmed by millions of other people's queries. But if the Quad9 headline made you want to *own* your resolution rather than rent it, recursive is the thing you're missing.

---

## The Decision Table: Unbound vs. Technitium vs. AdGuard Home

There are more DNS resolvers than anyone needs, but for the self-hosted recursive use case, three genuinely matter. Here's the honest comparison, because each one has a real job and none of them is the "right" answer for everyone.

| | **Unbound** | **Technitium DNS Server** | **AdGuard Home** |
|---|---|---|---|
| **What it is** | A battle-tested recursive resolver, written in C, developed by NLnet Labs | A full DNS server suite (recursive *and* authoritative) with a web UI, written in C# | An ad-blocking DNS forwarder with a polished dashboard |
| **Recursive by default?** | Yes — this is its core identity | Yes, but you can also run it as a forwarder | No — it's a forwarder; recursion isn't what it's for |
| **Ad/tracker blocking** | No (it's *just* a resolver) | Basic, via built-in blocking zones | Excellent — this is its reason to exist |
| **Web UI** | None (CLI/config file) | Full-featured, genuinely nice | Polished and user-friendly |
| **DNSSEC validation** | Yes, first-class | Yes | Validates upstream, not a full recursive validator |
| **DoH / DoT server** | Via `unbound`'s `https-port` / `tls-port` (and needs certs) | Built-in, including DoH/DoT/DoQ, with easy cert handling | Built-in DoH/DoT, easy |
| **Resource footprint** | Tiny — runs comfortably in 64MB | Heavier (C#/.NET), needs a few hundred MB | Light to moderate |
| **Best for** | The purist who wants a rock-solid recursive resolver and nothing else | The person who wants recursion *and* a web UI, authoritative zones, and filtering in one box | The person who wants ad blocking first, DNS privacy second |
| **My take** | The "own your DNS" answer, full stop | The best "one server for everything DNS" option | Better as a Pi-hole replacement than a resolver replacement |

Let me pull the threads on the two that actually matter for *this* post.

### Unbound: the purist's resolver

Unbound is the thing the "self-host your DNS" crowd means when they say it without further qualification. It's not an ad blocker, it doesn't have a dashboard, and it won't do anything except resolve names and validate DNSSEC — which is precisely why it's the right tool when the goal is "stop depending on a third party." It's small, it's fast, it's been around for two decades, and its configuration is a single well-documented file.

The honest downside is that it's *just* a resolver. If you also want a UI, or blocklists, or a pretty chart of what's being queried, Unbound says no. You pair it with something else (often Pi-hole in front of it as a filter, with Unbound as the recursive backend — a genuinely common and good pattern).

### Technitium: the full DNS suite

Technitium is the sleeper here and honestly my favorite for a homelab. It's a complete DNS server — recursive *and* authoritative, with DNSSEC, DoH, DoT, DoQ, a real web UI, and built-in blocking — all in a single C# application you can run in Docker. It's heavier than Unbound (you'll want a few hundred MB of RAM, not 64MB), but it gives you the "own your resolution" property *and* the usability that Unbound deliberately lacks.

If you want one container that does recursion, filtering, a dashboard, and even hosts your own `*.homelab` zones, Technitium is the answer. The only reason it doesn't win this post outright is that it's more moving parts than Unbound, and "more moving parts" is its own kind of risk when the whole point is reliability.

### AdGuard Home: great, but it's not a resolver

I have to be careful here, because AdGuard Home is excellent at what it does — but what it does is *filter and forward*, not resolve. It's a better Pi-hole in many ways (nicer UI, DoH/DoT built in, strong blocklist support), but under the hood it's still sending your queries upstream to Cloudflare or Quad9 unless you configure it otherwise. Using AdGuard Home "for DNS privacy" while pointing it at Quad9 means the Quad9 story is still *your* story. It's a Pi-hole replacement, not a resolver replacement, and it belongs in this table mostly so we can be honest about the difference.

---

## The Setup: Unbound in Five Minutes

If the goal is "own your DNS," the cleanest start is Unbound as a recursive resolver. Here's a working config, and it's genuinely short because Unbound's defaults are already sane.

### Docker Compose

```yaml
# docker-compose.yml
services:
  unbound:
    image: mvance/unbound:latest
    container_name: unbound
    restart: unless-stopped
    ports:
      - "53:53/tcp"
      - "53:53/udp"
    volumes:
      - ./unbound:/opt/unbound/etc/unbound
    healthcheck:
      test: ["CMD", "unbound-control", "status"]
      interval: 30s
      timeout: 10s
      retries: 3
```

The `mvance/unbound` image is the most widely used, actively maintained Unbound image, and it runs as a non-root user by default (which matters — DNS servers are a target, and running unprivileged is free hardening). Create the config directory and drop in a minimal `unbound.conf`:

```bash
mkdir -p unbound
```

### `unbound/unbound.conf`

```conf
server:
    # Listen on all interfaces inside the container
    interface: 0.0.0.0
    interface: ::0

    # Allow queries from your LAN / Docker network
    access-control: 192.168.0.0/16 allow
    access-control: 172.16.0.0/12 allow
    access-control: 10.0.0.0/8 allow

    # Recursion is the whole point
    do-ip4: yes
    do-ip6: yes
    do-udp: yes
    do-tcp: yes

    # DNSSEC validation on
    auto-trust-anchor-file: "/opt/unbound/etc/unbound/root.key"

    # Privacy settings
    hide-identity: yes
    hide-version: yes
    qname-minimisation: yes

    # Reasonable cache sizes
    cache-min-ttl: 300
    cache-max-ttl: 86400
    prefetch: yes

    # Hardening
    unwanted-reply-threshold: 10000
    do-not-query-localhost: no
    val-clean-additional: yes
    val-permissive-mode: no
```

The lines worth explaining, because they're the ones doing the "privacy" work:

- **`qname-minimisation: yes`** is the big one. It means Unbound sends the *minimum* amount of your query to each server it talks to — the root servers only see "I'm interested in `com`", not "I'm looking up `some-embarrassing-domain.com`". This is the single most important privacy setting in recursive DNS.
- **`auto-trust-anchor-file`** points at the DNSSEC root key, which is how Unbound validates every answer it gets. It's the difference between "trusting whatever the network says" and "verifying the chain of trust."
- **`hide-version` / `hide-identity`** stop Unbound from announcing its software version, which is minor but free.

Start it:

```bash
docker compose up -d
```

### Point a device at it (test first, don't switch the whole network blindly)

Before you move your router's DNS over, test with a single client:

```bash
dig @<your-server-ip> example.com
dig @<your-server-ip> example.com +dnssec
```

If the first returns an answer and the second shows `ad` (authenticated data) in the flags, you have a working, validating, recursive resolver. Now point your router's DNS at it — or, better, point your [WireGuard + Pi-hole](/blog/2026-04-21-wireguard-pihole-privacy-stack/) setup at it as the upstream.

---

## Where This Fits With What You Already Run

I want to be explicit about how this composes with the existing posts on this site, because "run Unbound" and "run Pi-hole" sound like they conflict and they absolutely don't.

The clean pattern, and the one I'd actually recommend:

```
Your device
    │
    ▼
Pi-hole  (blocklists, local records, cache)  ←  what you already run
    │
    ▼
Unbound  (recursive, DNSSEC-validating)  ←  what this post adds
    │
    ▼
Root servers → TLD servers → authoritative servers
```

Pi-hole stays the friendly front end — the blocklists, the local DNS records, the `plex.homelab` shortcuts, the admin dashboard. You just change its *upstream* from Cloudflare/Quad9 to your own Unbound instance (in Pi-hole: **Settings → DNS → uncheck everything, add a custom upstream pointing at your Unbound IP, port 53**). Now your ad blocking and your DNS ownership are both real: Pi-hole filters, Unbound resolves, and no third party sees your full query stream.

Or, if you'd rather consolidate: run **Technitium** instead and get the blocklists, the dashboard, and the recursion in a single box, at the cost of a heavier container and a bit more configuration surface. Both are legitimate; the choice is "two small, specialized tools" versus "one bigger, general tool."

---

## The Honest Downsides (Because This Isn't a Cheerleading Post)

Running your own resolver is real infrastructure, and I'd be doing you a disservice if I pretended otherwise.

- **Your cache starts cold.** Cloudflare's resolver has answered a billion queries and has every hot domain pre-warmed. Your Unbound starts empty, so your *first* query for any given domain takes the full recursive walk (a few hundred milliseconds). Once warm, it's fast — but a tiny homelab cache means fewer hits than a giant shared one. This is the single biggest real-world tradeoff, and it's why "recursive is always faster" is a lie.
- **You're now responsible for patching it.** Unbound has had CVEs. A public recursive resolver is a target, and if you don't keep the container updated, you've swapped a reliable upstream for an unpatched service. The `mvance/unbound` image helps here (watchtower or a monthly pull), but it's now *your* job.
- **No anycast, no failover.** Quad9 and Cloudflare are huge anycast networks that survive datacenter outages. Your single resolver is a single point of failure. If your box goes down, so does your DNS — and "DNS is down" presents as "the entire internet is down," which is a uniquely bad failure mode.
- **It doesn't hide you from your ISP.** This is important and widely misunderstood. A recursive resolver keeps your *full query stream* out of a third party's hands, but your ISP still sees the IP addresses you connect to afterward. Recursive DNS is about not handing one company a complete list of every domain you visit; it is *not* anonymity, and it's not a VPN. If you want the connection itself hidden, that's the [WireGuard](/blog/2026-04-21-wireguard-pihole-privacy-stack/) problem, not the resolver problem.

None of these are reasons not to do it — but they're the reasons to do it *deliberately*, with updates and a fallback, rather than as a set-and-forget experiment.

---

## The Verdict

Quad9 exiting France isn't a story about copyright. It's a reminder that "private DNS" is only private as long as the company running it stays private, solvent, and un-coerced — and those are all promises, not properties. The moment a resolver is *someone else's*, your resolution is a privilege, not something you own.

The fix is the thing homelabbers keep proving true about every other service: **run it yourself.** Unbound gives you a recursive, DNSSEC-validating resolver in a five-minute container, and the entire point is that it talks to the root servers directly — no upstream, no court order, no terms of service that can change underneath you. Pair it with the Pi-hole you already run, or consolidate with Technitium if you want a UI, and you've turned "I rent my DNS" into "I own my DNS."

It's not anonymity, it's not faster on a cold cache, and it comes with real maintenance. But the next time a resolver you don't control gets a court order, you'll read the headline, check your own `dig`, and shrug. That's the whole point.

**Resources:**
- [Unbound (NLnet Labs)](https://nlnetlabs.nl/projects/unbound/about/)
- [Technitium DNS Server](https://technitium.com/dns/)
- [AdGuard Home](https://adguard-dns.io/)
- [mvance/unbound Docker image](https://github.com/MatthewVance/unbound-docker)
- [WireGuard + Pi-hole (the companion post)](https://devhandbook.io/blog/wireguard-pihole-complete-privacy-stack/)

---

*Running your own resolver, or sticking with a public upstream? Found a blocklist or a Technitium config worth sharing? Drop it in the [Discord](https://discord.gg/selfhosted) — always curious how people are owning their DNS.*
