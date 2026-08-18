---
layout: post.njk
title: "Self-Hosted Git in 2026: Gitea vs Forgejo vs GitLab — Your Exit Ramp from GitHub"
date: 2026-08-18
description: "GitHub's trust problem is real, and the self-hosted Git options have never been better. Gitea, Forgejo, and GitLab all give you a full GitHub replacement on your own hardware — but they're not the same tool, and the choice matters more than the marketing lets on. Here's a practical comparison for people actively looking for a way out."
tags: ["self-hosted", "git", "gitea", "forgejo", "gitlab", "github", "homelab", "devops", "codeberg", "version-control"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-18-self-hosted-git-gitea-forgejo-gitlab"
---

There's a signal I've been watching for a while now, and it finally got loud enough that I can't ignore it.

A few weeks back, an "Ask HN: Alternatives to GitHub" thread hit 536 points and stayed on the front page for most of a day. Right around the same time, "GitHub down again" racked up 288 points. These aren't isolated blips. They're part of a slow, steady drumbeat of developers asking the same question in different words: *what happens when the platform I've built my entire workflow on stops being something I trust?*

The reasons people give vary. Some are worried about GitHub's increasingly aggressive AI training posture and the creeping sense that your private repos are being mined. Some are tired of the outages. Some just want to own their own infrastructure the way they own their own [email](/blog/2026-08-16-self-hosted-email-2026-stack-that-delivers-to-gmail) and their own [auth](/blog/2026-08-08-self-hosted-auth-sso-showdown). The common thread is the same: **people want an exit ramp, and they're not sure which one to take.**

This site has never covered self-hosted Git. That's a gap, and it's a weird one, because Git is the single most fundamental piece of a developer's toolchain. So let's fix it. This is a practical comparison of the three real options — Gitea, Forgejo, and GitLab — for someone who's actively looking for a way off GitHub and onto their own hardware.

## Why This Matters Now

Before I get into the tools, let me be clear about what's actually driving this, because it changes what you should optimize for.

The GitHub trust crisis isn't one thing. It's a bundle of anxieties that have been compounding:

- **AI training on your code.** GitHub has been increasingly opaque about what happens to the code in your repos, and the Copilot training question has never been answered to a lot of people's satisfaction. Whether or not your private repos are being used, the *uncertainty* is corrosive.
- **Outages and reliability.** GitHub is a massive, complex platform, and it goes down more than its marketing would like you to believe. When your CI, your issues, your PRs, and your code review all live in one place, an outage there is an outage everywhere.
- **Centralization risk.** One company, one account, one set of terms of service. If your account gets flagged, suspended, or caught in some automated moderation net, you can lose access to *everything* with almost no recourse. That's a single point of failure that a lot of developers are finally getting uncomfortable with.
- **The general self-hosting momentum.** This site has documented the broader trend for months — people are pulling their [photos](/blog/2026-06-17-immich-photo-management-homelab), their [music](/blog/2026-05-16-self-hosted-music-navidrome-soulseek), their [office suite](/blog/2026-08-14-self-hosted-office-suites-bento-onlyoffice-collabora), and their [calendar](/blog/2026-06-26-self-hosted-calendar-tools-homelab) back onto their own hardware. Git is just the next logical domino.

The good news is that the self-hosted Git landscape has never been stronger. The bad news is that the choice isn't obvious, and the wrong pick can leave you with a bloated monster you resent maintaining.

## The Three Contenders

Let me introduce the field, because the naming and history here is genuinely confusing if you haven't been following it.

### Gitea — the lightweight workhorse

[Gitea](https://gitea.io) is a self-hosted Git service written in Go. It's a single binary, it runs on a Raspberry Pi, and it gives you repos, issues, pull requests, wikis, releases, and a web UI that looks and feels a lot like GitHub. It's been around since 2016, it's battle-tested, and it's the default answer when someone asks "what's a lightweight self-hosted GitHub?"

Gitea's superpower is that it's *small*. A single Go binary, a SQLite or Postgres database, and you're done. It uses a fraction of the resources of GitLab, and it's genuinely pleasant to administer. For a solo developer or a small team, it's often everything you need and nothing you don't.

The asterisk on Gitea is its governance history. In 2022, the project's leadership moved it under a for-profit company, which triggered a community fork. That fork is Forgejo. More on that in a second.

### Forgejo — the community fork

[Forgejo](https://forgejo.org) is a fork of Gitea created in late 2022 by a group of developers (including the team behind Codeberg) who were uncomfortable with Gitea's move toward corporate control. It's a "soft fork" — it tracks Gitea's codebase but is governed by a non-profit, community-owned structure rather than a company.

Functionally, Forgejo and Gitea are nearly identical. They share the same core, the same UI, the same feature set. The difference is philosophical: Forgejo is explicitly committed to staying community-governed and non-profit, which matters to a lot of people who are leaving GitHub *because* of corporate control concerns. If your motivation for self-hosting Git is "I don't want a company owning my code platform," then Forgejo's governance is a feature, not a footnote.

Forgejo is also the engine behind [Codeberg](https://codeberg.org), the non-profit, EU-hosted GitHub alternative that's become the de facto home for a lot of open-source projects fleeing GitHub. If you've heard of Codeberg, you've heard of Forgejo.

### GitLab — the full platform

[GitLab](https://gitlab.com) is the heavyweight. It's not just a Git host — it's a complete DevOps platform with built-in CI/CD, container registry, package registry, security scanning, project management, and a dozen other things. The self-hosted version (GitLab CE, the Community Edition) is free and open-source, but it's a *big* piece of software.

GitLab's superpower is that it's a one-stop shop. If you want your code, your CI, your issues, your deployments, and your monitoring all in one place, GitLab does that. The trade-off is that it's heavy — it wants a real server with real resources, it's more complex to administer, and it's overkill for a lot of solo developers.

There's also a governance asterisk here too: GitLab is a publicly-traded company, and while the CE edition is open-source, the project's direction is ultimately corporate. For people fleeing GitHub over corporate-control concerns, GitLab can feel like trading one company for another.

## The Comparison

Let me actually compare them on the axes that matter for someone making this decision.

### Resource footprint

This is the first thing to know, because it determines whether you can even run the thing on your existing hardware.

- **Gitea / Forgejo:** Tiny. A single Go binary, ~50-100MB of RAM at idle, runs happily on a Raspberry Pi or a small LXC container. You can run it on the same box as a dozen other services and never notice it.
- **GitLab:** Heavy. The full GitLab CE stack wants 4GB of RAM *minimum* (8GB recommended), a real CPU, and a Postgres database. It's not a "toss it on the Pi" kind of tool. It needs its own VM or a beefy container.

If you're running a modest homelab, this alone often decides it. Gitea or Forgejo will slot into your existing setup invisibly. GitLab will demand a dedicated slice of your hardware.

### Feature set

- **Gitea / Forgejo:** Repos, issues, pull requests, wikis, releases, code search, webhooks, and a solid API. That's the core GitHub experience. What they *don't* have is built-in CI/CD — you pair them with an external runner (Gitea Actions, which is GitHub-Actions-compatible, or a separate CI tool like Drone or Woodpecker).
- **GitLab:** Everything above, plus built-in CI/CD (GitLab Runner), a container registry, a package registry, security scanning, code review tools, and project management boards. It's a full platform, not just a Git host.

The honest framing: Gitea and Forgejo give you *GitHub the code host*. GitLab gives you *GitHub plus GitHub Actions plus a bunch of other stuff*, all in one box. Whether you need that "plus" is the real question.

### CI/CD

This is where the biggest practical difference lives.

- **Gitea / Forgejo:** You bring your own CI. Gitea has "Gitea Actions," which is compatible with GitHub Actions syntax, but it requires you to run a separate `act_runner` service. Forgejo has the same thing (Forgejo Actions). It works, but it's an extra moving part to set up and maintain.
- **GitLab:** CI/CD is built in and first-class. You write a `.gitlab-ci.yml`, register a runner, and you're done. It's the most mature self-hosted CI story of the three, and it's a big part of why people choose GitLab despite the resource cost.

If CI/CD is central to your workflow, GitLab has a real edge. If you're fine with a lightweight external runner or you don't need CI at all, Gitea/Forgejo are perfectly adequate.

### Governance and trust

This is the axis that's easy to dismiss and hard to overstate, given *why* people are leaving GitHub.

- **Gitea:** Governed by a for-profit company (Gitea Ltd). The code is open-source (MIT), but the project's direction is corporate. This is the exact thing that triggered the Forgejo fork.
- **Forgejo:** Governed by a non-profit, community-owned structure. Explicitly committed to staying that way. If "I don't want a company owning my code platform" is your motivation, Forgejo is the answer.
- **GitLab:** Governed by a publicly-traded company. The CE edition is open-source, but the roadmap is corporate, and there's a long history of features being gated behind the paid tiers.

Here's the uncomfortable truth: if you're leaving GitHub because you don't trust a corporation with your code, Gitea and GitLab both ask you to trust a *different* corporation. Forgejo is the only one of the three that's structurally committed to community ownership. That's not a small thing.

### Migration path

How hard is it to actually move your stuff?

- **Gitea / Forgejo:** Both have a built-in "migrate from GitHub" feature that pulls your repos, issues, PRs, and wikis with a few clicks. It's genuinely easy. You can also mirror repos so they stay in sync with GitHub while you transition.
- **GitLab:** Also has a GitHub importer, and it's solid. The migration story is comparable.

All three make the *initial* move easy. The harder part is the *ongoing* stuff — your CI configs, your webhooks, your integrations — and that's where GitLab's all-in-one nature can actually help, because you're migrating to a platform that has its own equivalents for everything.

### The Decision Matrix

| | **Gitea** | **Forgejo** | **GitLab CE** |
|---|---|---|---|
| **License** | MIT | MIT (GPL for some parts) | MIT (CE) |
| **Governance** | For-profit company | Non-profit community | Public company |
| **Resource footprint** | Tiny (~100MB RAM) | Tiny (~100MB RAM) | Heavy (4GB+ RAM) |
| **Core Git features** | ✅ | ✅ | ✅ |
| **Built-in CI/CD** | ❌ (external runner) | ❌ (external runner) | ✅ (first-class) |
| **Container/package registry** | ❌ | ❌ | ✅ |
| **GitHub migration** | ✅ | ✅ | ✅ |
| **Single binary** | ✅ | ✅ | ❌ (full stack) |
| **Best for** | Solo devs, small teams | Community-minded self-hosters | Teams that want a full platform |

## My Actual Recommendation

Here's where I land, and I'll be direct about it.

**If you're a solo developer or a small team who just wants your code off GitHub: use Forgejo.** It's lightweight, it's community-governed, and it does everything you actually need. The fact that it's the engine behind Codeberg means it's got a real community and a real future. The only reason to pick Gitea over Forgejo is if you specifically want the corporate-backed version, and given *why* you're leaving GitHub, you probably don't.

**If you need built-in CI/CD and a full DevOps platform: use GitLab CE.** It's heavy, but it's the most complete self-hosted Git experience you can get, and the CI story is genuinely best-in-class. Just go in with your eyes open about the resource cost and the corporate governance. Give it its own VM with 8GB of RAM and don't look back.

**If you're not ready to fully self-host: use Codeberg.** It's Forgejo hosted for you, by a non-profit, in the EU. It's the lowest-friction way to get off GitHub without running your own server, and it's a great stepping stone. You can always migrate to self-hosted Forgejo later — the data is yours and the format is portable.

**What I would *not* do is pick Gitea over Forgejo without a specific reason.** They're functionally identical, and Forgejo has the better governance story. The fork exists precisely because a lot of people cared about that, and if you're in the "I don't trust a company with my code" camp, you're one of those people.

## The Setup, Briefly

For the people who want to actually do this today, here's the short version. Forgejo (and Gitea) run beautifully in Docker:

```yaml
# docker-compose.yml
services:
  forgejo:
    image: codeberg.org/forgejo/forgejo:latest
    container_name: forgejo
    restart: unless-stopped
    environment:
      - USER_UID=1000
      - USER_GID=1000
    volumes:
      - ./forgejo:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "3000:3000"
      - "2222:22"
```

Then `docker compose up -d`, visit `http://your-server:3000`, and run through the installer. Point it at a Postgres or SQLite database, set your domain, and you're live. Put it behind a [Cloudflare Tunnel](/blog/2026-07-26-cloudflare-tunnels-homelab-guide) and your [SSO of choice](/blog/2026-08-08-self-hosted-auth-sso-showdown), and you've got a GitHub replacement that's genuinely yours.

GitLab is a bigger lift — it has an official Docker image, but you'll want to read the docs and give it real resources. It's not a "five-minute setup" tool the way Forgejo is.

## The Bottom Line

The GitHub trust crisis is real, and it's not going away. The good news is that the exit ramp has never been better paved. Forgejo gives you a lightweight, community-owned GitHub replacement that runs on a Raspberry Pi. GitLab gives you a full DevOps platform if you're willing to feed it. And Codeberg gives you a hosted middle ground if you're not ready to run your own server.

The one thing I'd urge you to actually think about is *why* you're leaving. If it's about features, GitLab is the most complete. If it's about resources, Forgejo is the lightest. But if it's about trust — about not wanting a corporation to own the platform your code lives on — then the answer is Forgejo, and it's not particularly close. The fork exists for exactly this reason.

Your code is the most important thing you'll ever self-host. It's worth getting the governance right.

---

*Are you running self-hosted Git, or are you still on the fence? I'm genuinely curious where people land on the Gitea-vs-Forgejo question specifically — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my posts on [self-hosted SSO](/blog/2026-08-08-self-hosted-auth-sso-showdown) and [Cloudflare Tunnels](/blog/2026-07-26-cloudflare-tunnels-homelab-guide).*
