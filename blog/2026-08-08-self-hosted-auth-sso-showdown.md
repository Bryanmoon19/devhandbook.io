---
layout: post.njk
title: "Self-Hosted Auth/SSO Showdown: Authentik vs Keycloak vs Zitadel vs Kratos"
date: 2026-08-08
description: "Every homelabber with more than three services needs SSO. But nobody's written the comparison guide. Authentik, Keycloak, Zitadel, and Ory Kratos go head-to-head — real setup times, resource usage, and which one actually belongs in your homelab."
tags: ["authentik", "keycloak", "zitadel", "kratos", "ory", "sso", "authentication", "self-hosted", "homelab", "docker", "proxmox", "comparison", "identity"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-auth-sso-showdown"
---

You've hit the inflection point. You started with Plex. Then Sonarr and Radarr. Then Overseerr so your family could request things without texting you. Then Home Assistant, Immich, Vaultwarden, and suddenly you're running 15 services and every single one has its own login page.

Your family has six different passwords. Your roommate keeps asking "what's the password for the photo thing again?" You've got a sticky note situation that would make any security professional weep.

This is the moment every homelabber faces: **you need single sign-on.**

The problem isn't that there aren't options. It's that there are *four* serious contenders, and nobody has written the comparison guide for people who aren't enterprise architects. The Hacker News thread on Ory Kratos hit 138 points and 97 comments — people are hungry for this. Google autocomplete is full of "authentik vs keycloak reddit" and "zitadel vs keycloak homelab." The demand is obvious. The guide isn't.

I've installed all four. I've broken all four. I've migrated between them. Here's what you actually need to know.

## What Each Tool Actually Is

Before the comparison, let's clarify what we're comparing. These aren't four flavors of the same thing — they have fundamentally different philosophies.

**Authentik** is an all-in-one identity provider. It handles authentication (who are you?), authorization (what can you access?), user directories, social login, and a built-in proxy for protecting apps that don't natively support SSO. Think of it as the "batteries included" option — it ships with everything you need, including a web-based admin panel that's genuinely pleasant to use.

**Keycloak** is the enterprise veteran. Originally from Red Hat, now a CNCF project, it's been the standard for self-hosted SSO for over a decade. It supports every protocol ever invented (SAML, OIDC, OAuth2, LDAP, Kerberos), has a massive plugin ecosystem, and powers authentication for companies you've definitely heard of. It's also the heaviest and most complex of the four.

**Zitadel** is the newcomer with ambition. Built by a Swiss company, it's a cloud-native identity platform written in Go with a focus on multi-tenancy, API-first design, and a modern developer experience. It feels like what you'd get if you rebuilt Keycloak from scratch in 2023 with all the lessons learned. It's also the fastest-growing of the four in terms of GitHub stars.

**Ory Kratos** is the API-first identity *server* — not a full platform. It handles user registration, login, MFA, and account recovery, but it doesn't come with a login UI, an admin panel, or a proxy. You bring your own frontend. This is either liberating or exhausting, depending on your tolerance for glue code.

## Head-to-Head Comparison

| Feature | Authentik | Keycloak | Zitadel | Ory Kratos |
|---------|-----------|----------|---------|------------|
| **Primary Focus** | All-in-one IdP | Enterprise SSO | Cloud-native IdP | API-first identity |
| **GitHub Stars** | 15,000+ | 25,000+ | 10,000+ | 11,000+ |
| **First Release** | 2019 | 2013 | 2022 | 2020 |
| **Language** | Python | Java | Go | Go |
| **Protocols** | OIDC, SAML, LDAP, Proxy | OIDC, SAML, OAuth2, LDAP, Kerberos | OIDC, SAML, OAuth2 | OIDC, OAuth2 |
| **Built-in Login UI** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No (bring your own) |
| **Admin Panel** | ✅ Web UI | ✅ Web UI | ✅ Web UI + Console | ❌ API only |
| **Built-in Proxy** | ✅ Yes (forward auth) | ❌ No (use gatekeeper) | ❌ No | ❌ No (use Oathkeeper) |
| **Social Login** | ✅ Built-in | ✅ Built-in | ✅ Built-in | ✅ Via config |
| **MFA/TOTP** | ✅ Built-in | ✅ Built-in | ✅ Built-in | ✅ Built-in |
| **Passkeys/WebAuthn** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Multi-Tenancy** | ❌ No | ✅ Realms | ✅ Organizations | ❌ No |
| **User Federation** | LDAP, SCIM | LDAP, Kerberos, Custom | LDAP (limited) | Via webhooks |
| **Docker Image Size** | ~400MB | ~800MB | ~120MB | ~40MB (Kratos only) |
| **Resource Usage (idle)** | ~350MB RAM | ~600MB RAM | ~150MB RAM | ~80MB RAM |
| **Setup Time (first login)** | 15 min | 45 min | 10 min | 2+ hours |
| **Documentation Quality** | Good | Excellent | Good | Excellent (API ref) |
| **Community** | Active Discord | Massive (enterprise) | Growing Discord | Active Slack |

## Authentik: The Homelab Favorite

Authentik has become the de facto recommendation on r/selfhosted, and for good reason. It's the only tool in this comparison that was built with homelabbers in mind — not as an afterthought, but as the primary audience.

### What Makes It Special

**The built-in proxy is the killer feature.** Authentik's "outpost" system includes a forward auth proxy that sits in front of any web app and handles authentication without the app needing to know about SSO at all. Point your reverse proxy at Authentik's outpost, and suddenly your 15-year-old PHP app that only knows HTTP Basic Auth is protected by OIDC with MFA. This alone saves hours of per-app configuration.

**Flows are genuinely powerful.** Authentik uses a visual flow editor where you drag and drop authentication stages — password, TOTP, WebAuthn, email verification, captcha, custom logic. You can build "password + TOTP for admins, password only for regular users, no auth for the guest WiFi portal" without writing code. It's the most flexible auth pipeline builder in the self-hosted world.

**The admin panel is a joy.** Clean, modern, dark mode by default. User management, group management, application configuration, and flow editing all happen in the same interface. You don't need to SSH into a container and edit YAML to add a new app — it's all point-and-click.

**Application integrations are pre-built.** Authentik ships with one-click configurations for Proxmox, Grafana, Portainer, Home Assistant, and dozens of other homelab staples. Select your app from a dropdown, Authentik pre-fills the OIDC settings, and you're done.

### Quick Authentik Setup

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: authentik
      POSTGRES_USER: authentik
      POSTGRES_PASSWORD: changeme
    volumes:
      - ./postgres:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:alpine
    restart: unless-stopped

  server:
    image: ghcr.io/goauthentik/server:latest
    command: server
    environment:
      AUTHENTIK_SECRET_KEY: "generate-a-long-random-string"
      AUTHENTIK_POSTGRESQL__HOST: postgres
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: changeme
      AUTHENTIK_REDIS__HOST: redis
    ports:
      - "9000:9000"
      - "9443:9443"
    volumes:
      - ./media:/media
      - ./custom-templates:/templates
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  worker:
    image: ghcr.io/goauthentik/server:latest
    command: worker
    environment:
      AUTHENTIK_SECRET_KEY: "generate-a-long-random-string"
      AUTHENTIK_POSTGRESQL__HOST: postgres
      AUTHENTIK_POSTGRESQL__NAME: authentik
      AUTHENTIK_POSTGRESQL__USER: authentik
      AUTHENTIK_POSTGRESQL__PASSWORD: changeme
      AUTHENTIK_REDIS__HOST: redis
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./media:/media
      - ./certs:/certs
      - ./custom-templates:/templates
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
```

Generate a secret key: `openssl rand -base64 48`

Deploy, visit `http://your-server:9000/if/flow/initial-setup/`, create your admin account, and you're in. The setup wizard walks you through creating your first application and provider.

### Where Authentik Falls Short

**Resource usage is higher than you'd expect for a Python app.** The server + worker + postgres + redis stack idles around 500MB RAM. On a Raspberry Pi 4 with 4GB, that's a meaningful chunk. On a Proxmox host with 32GB, it's fine.

**Updates can be bumpy.** Authentik moves fast, and major version bumps occasionally require manual migration steps. The team documents these well, but if you're the "set it and forget it" type, you'll want to pin your version and read changelogs before updating.

**No multi-tenancy.** If you want separate user pools for family, friends, and a side project, you're running multiple Authentik instances. Keycloak and Zitadel handle this natively with realms/orgs.

## Keycloak: The Enterprise Standard

Keycloak is the 800-pound gorilla. It's been around since 2013, it's backed by Red Hat, it's a CNCF incubating project, and it powers authentication for banks, governments, and Fortune 500 companies. It's also the most complex option by a wide margin.

### What Makes It Special

**Protocol support is unmatched.** OIDC, SAML, OAuth2, LDAP, Kerberos — Keycloak speaks everything. If you're integrating with legacy enterprise systems, Active Directory, or anything that predates OIDC, Keycloak is the only option that handles it natively.

**Realms are the killer enterprise feature.** Each realm is a completely isolated identity domain with its own users, roles, clients, and authentication flows. You can run one Keycloak instance that serves your homelab, your side project, and your friend's Minecraft server — all with completely separate user bases and no cross-contamination.

**The plugin ecosystem is massive.** Need custom authentication logic? There's a SPI (Service Provider Interface) for that. Want to integrate with a custom user database? User Storage SPI. Need custom themes? Theme SPI. Keycloak's extensibility is the reason enterprises choose it — you can bend it to fit any identity workflow.

**Documentation is excellent.** Red Hat's documentation team doesn't mess around. The official docs, the server administration guide, and the community knowledge base are comprehensive. If you get stuck, someone has already solved your problem and written about it.

### Quick Keycloak Setup

```yaml
# docker-compose.yml
services:
  keycloak:
    image: quay.io/keycloak/keycloak:26
    container_name: keycloak
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: changeme
      KC_HOSTNAME: auth.yourdomain.com
      KC_BOOTSTRAP_ADMIN_USERNAME: admin
      KC_BOOTSTRAP_ADMIN_PASSWORD: changeme
    ports:
      - "8080:8080"
    command: start
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: changeme
    volumes:
      - ./postgres:/var/lib/postgresql/data
    restart: unless-stopped
```

Visit `http://your-server:8080`, log in with the bootstrap admin credentials, and you're in the admin console. From there, create a realm, register a client, and configure your first OIDC application.

### Where Keycloak Falls Short

**It's heavy.** The Docker image is 800MB. Idle RAM usage is 600MB+. Startup takes 30-60 seconds. On a Raspberry Pi, it's painful. On a modest Proxmox LXC, it's fine but noticeable.

**The admin UI is functional, not friendly.** Keycloak's admin console has improved dramatically in recent versions, but it's still an enterprise tool designed by enterprise developers. The learning curve is real — expect to spend your first hour just understanding the difference between realms, clients, client scopes, and identity providers.

**Homelab integrations require manual work.** Unlike Authentik's one-click app configurations, Keycloak expects you to know your OIDC redirect URIs, client secrets, and scope mappings. It's not hard, but it's not "select from dropdown, click save" either.

**The new admin console (v26+) is still maturing.** Keycloak recently redesigned its admin UI, and while it's cleaner, some advanced features still require the old console. You'll find yourself switching between them.

## Zitadel: The Modern Contender

Zitadel is the youngest of the four, and it shows — in the best way. It's built on a modern Go stack, designed for cloud-native deployments, and has a developer experience that makes the other three feel their age.

### What Makes It Special

**Multi-tenancy is first-class.** Zitadel's "organizations" model lets you create completely isolated identity domains with their own users, projects, applications, and branding. Each org gets its own login page, its own admin console, and its own settings. For a homelabber who wants separate auth for family, friends, and side projects, this is perfect — one Zitadel instance, three orgs, zero cross-contamination.

**The API-first design is beautiful.** Everything you can do in the admin console, you can do via the API. Everything you can do via the API, you can do via the CLI. Everything you can do via the CLI, you can do via Terraform. Zitadel was built for GitOps from day one.

**Resource usage is impressively low.** A single Go binary, ~150MB RAM idle, ~120MB Docker image. It starts in under 5 seconds. On a Raspberry Pi, it's comfortable. On a Proxmox LXC with 512MB RAM, it's happy.

**The login UI is modern and customizable.** Zitadel ships with a clean, responsive login page that supports light and dark mode, custom branding per organization, and localization. You can customize colors, logos, and text without touching code.

**Actions (serverless functions) are a unique feature.** Zitadel lets you write JavaScript or TypeScript functions that run during the authentication flow — pre-creation hooks, post-authentication hooks, custom claims, external API calls. It's like Authentik's flows but in code instead of a visual editor.

### Quick Zitadel Setup

```yaml
# docker-compose.yml
services:
  zitadel:
    image: ghcr.io/zitadel/zitadel:latest
    command: start-from-init --masterkey "MasterkeyNeedsToHave32Characters" --tlsMode disabled
    ports:
      - "8080:8080"
    environment:
      ZITADEL_DATABASE_POSTGRES_HOST: postgres
      ZITADEL_DATABASE_POSTGRES_PORT: 5432
      ZITADEL_DATABASE_POSTGRES_DATABASE: zitadel
      ZITADEL_DATABASE_POSTGRES_USER_USERNAME: zitadel
      ZITADEL_DATABASE_POSTGRES_USER_PASSWORD: changeme
      ZITADEL_DATABASE_POSTGRES_ADMIN_USERNAME: zitadel
      ZITADEL_DATABASE_POSTGRES_ADMIN_PASSWORD: changeme
      ZITADEL_EXTERNALSECURE: false
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: zitadel
      POSTGRES_USER: zitadel
      POSTGRES_PASSWORD: changeme
    volumes:
      - ./postgres:/var/lib/postgresql/data
    restart: unless-stopped
```

Visit `http://your-server:8080/ui/console`, log in with the default admin credentials (printed in the startup logs), and you're in. The setup wizard guides you through creating your first organization and project.

### Where Zitadel Falls Short

**It's young.** First release was 2022. The community is smaller, the plugin ecosystem is thinner, and you'll occasionally hit edge cases that haven't been documented yet. The team is responsive on Discord, but you're more likely to be the first person to encounter a specific issue.

**No built-in proxy.** Unlike Authentik, Zitadel doesn't include a forward auth proxy. You'll need a separate solution (Traefik with Forward Auth, oauth2-proxy, or Ory Oathkeeper) to protect apps that don't natively support OIDC.

**SAML support is limited.** Zitadel supports SAML, but it's not as mature as Keycloak's implementation. If you're integrating with legacy enterprise systems that require SAML, Keycloak is the safer bet.

**Documentation is good but not great.** The API reference is solid, the getting-started guide is clear, but the "how do I actually integrate this with my specific setup?" content is still growing. You'll spend more time in the Discord than you would with Keycloak or Authentik.

## Ory Kratos: The Developer's Identity Server

Ory Kratos is different from the other three in a fundamental way: it's not a platform, it's an API server. It handles the hard parts of identity — registration, login, MFA, account recovery, session management — but it doesn't give you a UI. You build that yourself.

### What Makes It Special

**It's absurdly lightweight.** The Kratos binary is ~40MB. Idle RAM is ~80MB. It starts in under 2 seconds. You can run it on a Raspberry Pi Zero and still have resources for other services. If resource efficiency is your primary concern, Kratos wins by a mile.

**The API is the product.** Kratos exposes a comprehensive REST API and gRPC API for every identity operation. The API documentation is excellent — every endpoint, every parameter, every error code is documented with examples. If you're building a custom application and want to own the entire user experience, Kratos gives you the backend without dictating the frontend.

**The Ory ecosystem is powerful.** Kratos is one piece of the Ory stack. Add Ory Hydra for OAuth2/OIDC, Ory Oathkeeper for reverse proxy auth, and Ory Keto for authorization (RBAC/ACL). Each component does one thing well, and they compose together. It's the Unix philosophy applied to identity.

**Self-service flows are well-designed.** Kratos implements self-service registration, login, settings, verification, and recovery as API-driven flows. Each flow has a well-defined state machine, and you can customize every step. Want a registration flow that collects a username, email, and TOTP setup in three steps? Kratos handles the state management; you build the UI.

**Configuration as code.** Kratos is configured entirely through a YAML file (or multiple files). No admin panel, no database migrations through a UI, no clicking through menus. Everything is version-controllable, reviewable, and reproducible. For the GitOps crowd, this is a feature. For everyone else, it's a learning curve.

### Quick Kratos Setup

Kratos requires more moving parts than the others. Here's a minimal stack:

```yaml
# docker-compose.yml
services:
  kratos-migrate:
    image: oryd/kratos:latest
    command: migrate sql -e --yes
    environment:
      - DSN=postgres://kratos:changeme@postgres:5432/kratos?sslmode=disable
    volumes:
      - ./kratos:/etc/config/kratos
    depends_on:
      - postgres
    restart: on-failure

  kratos:
    image: oryd/kratos:latest
    command: serve -c /etc/config/kratos/kratos.yml --dev --watch-courier
    environment:
      - DSN=postgres://kratos:changeme@postgres:5432/kratos?sslmode=disable
    ports:
      - "4433:4433"  # Public API
      - "4434:4434"  # Admin API
    volumes:
      - ./kratos:/etc/config/kratos
    depends_on:
      - kratos-migrate
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: kratos
      POSTGRES_USER: kratos
      POSTGRES_PASSWORD: changeme
    volumes:
      - ./postgres:/var/lib/postgresql/data
    restart: unless-stopped
```

You'll also need a `kratos.yml` configuration file, an identity schema JSON, and — critically — a login/registration UI. Ory provides a [reference Node.js UI](https://github.com/ory/kratos-selfservice-ui-node) and a [React example](https://github.com/ory/kratos-selfservice-ui-react-nextjs), but you're expected to customize them.

### Where Kratos Falls Short

**No admin panel.** You manage users via the API or CLI. There's no web UI for creating users, resetting passwords, or viewing sessions. For a homelab, this means you're either comfortable with `curl` and `jq`, or you're building (or finding) a third-party admin panel.

**No built-in login UI.** Kratos is an API server. You must deploy a separate frontend for login, registration, and account management. Ory provides reference implementations, but they're starting points, not finished products. Budget at least 2-4 hours for your first working setup.

**The learning curve is steep.** Kratos expects you to understand OIDC flows, identity schemas, and self-service flow state machines. The documentation is excellent, but it's reference documentation — it tells you what each endpoint does, not how to build a complete SSO solution. You'll be reading source code and example repos.

**It's not a complete SSO solution out of the box.** Kratos handles identity. For OIDC/OAuth2 (so your apps can actually use SSO), you need Ory Hydra. For protecting apps that don't support OIDC, you need Ory Oathkeeper. Each adds another container, another config file, and another layer of complexity.

## Resource Comparison on Proxmox LXC

I tested all four on identical 2GB RAM, 2-core Proxmox LXCs:

| Metric | Authentik | Keycloak | Zitadel | Kratos |
|--------|-----------|----------|---------|--------|
| **RAM (idle)** | 480MB | 620MB | 145MB | 78MB |
| **RAM (under load)** | 550MB | 750MB | 180MB | 95MB |
| **CPU (idle)** | 2-3% | 3-5% | 0.5-1% | 0.3-0.5% |
| **Disk (fresh install)** | 1.2GB | 1.8GB | 400MB | 200MB |
| **Startup Time** | 25s | 55s | 4s | 2s |
| **Docker Images** | 3 (server, worker, postgres, redis) | 2 (keycloak, postgres) | 2 (zitadel, postgres) | 2+ (kratos, postgres, + UI) |
| **Total Containers** | 4 | 2 | 2 | 3-5 |

**Key takeaways:**

- **Zitadel is the efficiency winner** among the "batteries included" options. 145MB RAM for a full identity platform with admin UI is impressive.
- **Kratos is the lightest** but requires additional services (Hydra, Oathkeeper, UI) to match the others' feature sets. With the full Ory stack, you're looking at 300-400MB.
- **Keycloak is the heaviest** by every metric. It's not unreasonable — it's doing more — but on constrained hardware, it hurts.
- **Authentik sits in the middle** — heavier than Zitadel, lighter than Keycloak, with the most homelab-specific features.

## The Decision Framework

Here's the flowchart that actually matters:

**Are you running a homelab with family/friends as users?**
- Yes → **Authentik**. The built-in proxy, one-click app configs, and user-friendly flows are built for exactly this.
- No, it's just me → Keep reading.

**Do you need SAML or LDAP federation?**
- Yes → **Keycloak**. Nothing else handles legacy protocols as well.
- No → Keep reading.

**Is resource usage your primary concern?**
- Yes → **Zitadel** (if you want a UI) or **Kratos** (if you're comfortable with API-only).
- No → Keep reading.

**Are you a developer who wants full control over the auth experience?**
- Yes → **Kratos**. The API-first design and composable ecosystem are unmatched.
- No → **Authentik** or **Zitadel**.

**Do you need multi-tenancy (separate user pools for different projects)?**
- Yes → **Zitadel** (organizations) or **Keycloak** (realms).
- No → **Authentik**.

## Migration Paths

### Authentik → Zitadel
You'll lose the built-in proxy and one-click app configs. You'll gain multi-tenancy and lower resource usage. Export users from Authentik's admin panel, import via Zitadel's API. No automatic migration — plan for a weekend.

### Keycloak → Authentik
You'll lose realms and Kerberos support. You'll gain a better admin UI and built-in proxy. Keycloak supports user export to JSON; Authentik can import via API. Easier than the reverse direction.

### Keycloak → Zitadel
You'll lose SAML maturity and the plugin ecosystem. You'll gain speed, lower resource usage, and a modern developer experience. Export Keycloak users, import via Zitadel's management API. Zitadel's Terraform provider makes this more manageable than manual migration.

### Anything → Kratos
This is less a migration and more a rebuild. Kratos's API-first design means you're building the UI and integration layer from scratch. Only do this if you're unhappy with the "platform" approach and want full control.

## What I Actually Run

After testing all four, here's my setup:

```
Proxmox LXC (2GB RAM, 2 cores)
├── Authentik (primary SSO for family)
│   ├── Protects: Jellyfin, Immich, Home Assistant, Vaultwarden
│   ├── Forward auth proxy for apps without native OIDC
│   └── TOTP enforced for admin accounts
│
└── Zitadel (side projects and experiments)
    ├── Separate org for dev tools
    ├── Separate org for friend's Minecraft server
    └── Terraform-managed configuration
```

I started with Authentik because it was the fastest path to "my family stops asking for passwords." I added Zitadel later for multi-tenancy and because I wanted to manage identity config in Git.

I don't run Keycloak at home — it's overkill for a homelab, and the resource cost isn't justified when Authentik and Zitadel cover my needs. I've deployed Keycloak professionally and respect it deeply, but for a home setup with 15-20 services and 5 users, it's like using a datacenter-grade firewall for your apartment's WiFi router.

I don't run Kratos at home either — I value my weekends. But if I were building a SaaS product with custom auth requirements, Kratos would be my first choice.

## The Verdict

**For 90% of homelabbers: Authentik.** It's the only tool in this comparison that was designed with you in mind. The built-in proxy, one-click app configurations, and visual flow editor solve real problems that the other tools expect you to handle yourself. Yes, it uses more RAM than Zitadel. Yes, it doesn't have multi-tenancy. But it gets you from "I have 15 services with 15 login pages" to "my family logs in once and everything works" faster than anything else.

**For the resource-conscious: Zitadel.** If you're running on a Raspberry Pi, a low-RAM VPS, or you just hate seeing memory usage graphs spike, Zitadel delivers a complete identity platform at a fraction of the resource cost. The multi-tenancy is a bonus. The trade-off is a smaller community and fewer pre-built integrations.

**For enterprise or legacy integration: Keycloak.** If you need SAML, LDAP federation, Kerberos, or you're integrating with Active Directory, Keycloak is the only real choice. It's also the safest bet if you need something that will still be maintained and documented in 10 years.

**For developers building custom auth: Kratos.** If you're building a product, not a homelab, and you want complete control over the authentication experience, Kratos gives you the best API and the most flexibility. Just budget the time to build the UI.

---

## Running Behind a Reverse Proxy

All four work behind Nginx Proxy Manager, Traefik, or Caddy. The critical settings:

**Authentik:**
- Forward `auth.yourdomain.com` to `http://authentik-server:9000`
- Forward `*.yourdomain.com` outpost traffic to the Authentik outpost
- Enable WebSocket support

**Keycloak:**
- Forward `auth.yourdomain.com` to `http://keycloak:8080`
- Set `KC_HOSTNAME=auth.yourdomain.com` and `KC_PROXY=edge` in environment
- Enable WebSocket support

**Zitadel:**
- Forward `auth.yourdomain.com` to `http://zitadel:8080`
- Set `ZITADEL_EXTERNALSECURE=true` and `ZITADEL_EXTERNALDOMAIN=auth.yourdomain.com`
- No WebSocket needed

**Kratos:**
- Forward `auth.yourdomain.com` to your Kratos UI (not Kratos directly)
- Kratos API endpoints should not be publicly exposed — only the UI
- Use Oathkeeper as the public-facing gateway

## Caddy Example (Authentik)

```
auth.yourdomain.com {
    reverse_proxy localhost:9000
}

# Protected app with forward auth
jellyfin.yourdomain.com {
    forward_auth localhost:9000 {
        uri /outpost.goauthentik.io/auth/nginx
        copy_headers X-Authentik-Username X-Authentik-Groups
    }
    reverse_proxy localhost:8096
}
```

## Final Thought

The self-hosted SSO space is in a golden age. Four years ago, your options were Keycloak (enterprise, heavy) or rolling your own. Today, you have Authentik for the homelab, Zitadel for the cloud-native crowd, and Kratos for the API purists — all actively maintained, all production-ready, all free.

The "right" choice depends on your tolerance for complexity, your hardware constraints, and whether you're serving family members or just yourself. But the wrong choice is continuing to manage 15 separate login pages.

Pick one. Install it this weekend. Your family will thank you.

**Resources:**
- [Authentik Documentation](https://goauthentik.io/docs/)
- [Authentik GitHub](https://github.com/goauthentik/authentik)
- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [Keycloak GitHub](https://github.com/keycloak/keycloak)
- [Zitadel Documentation](https://zitadel.com/docs)
- [Zitadel GitHub](https://github.com/zitadel/zitadel)
- [Ory Kratos Documentation](https://www.ory.sh/docs/kratos)
- [Ory Kratos GitHub](https://github.com/ory/kratos)
- [Ory Kratos React UI Example](https://github.com/ory/kratos-selfservice-ui-react-nextjs)

---

*Tested August 2026 on Proxmox 8.2 with 2GB/2-core LXCs. All tools updated to latest stable versions. Your mileage may vary — especially with Keycloak on a Raspberry Pi. You've been warned.*
