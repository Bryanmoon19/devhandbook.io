---
layout: post.njk
title: "Self-Hosted This Week: Domains, Craft, and the Return of Tape — October 12–19, 2026"
date: 2026-10-19
description: "A registrar seizes a sysadmin's domains with no warning, Linear's founder makes the case for human craft over automated pipelines, a micron-scale 3D printer tops Hacker News, Dockge goes quiet and the community migrates to Arcane, and LTO tape comes back to the homelab. This week's roundup."
tags: ["selfhosted", "weekly", "homelab", "roundup", "domains", "3d-printing", "docker", "llm", "backup", "maintenance"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-10-19"
---

If last week was about the *people* behind the stack, this week is about the *ground* it stands on. Your domains. Your backups. The craft that makes good software good. A registrar yanked someone's entire domain portfolio with no warning. A founder wrote a quiet defense of the human being behind the product. A micron-scale 3D printer captured the maker imagination. And the homelab community, true to form, rediscovered magnetic tape.

The through-line: **the things you assume are solid — your registrar, your Docker tool, your hard drives — deserve a second look.** Here's what caught my eye from October 12–19, 2026.

---

## 1. Namecheap Seized and Disabled a Sysadmin's Entire Domain Portfolio

**What it is:** A [post on r/sysadmin](https://www.reddit.com/r/sysadmin/comments/1x8cycd/namecheap_just_seized_and_disabled_all_my_domains/) that exploded to the top of Hacker News this week (500+ points) describes a user logging in to find every single one of their Namecheap domains — "seized and disabled" — with no explanation and no recourse beyond a support ticket.

**Why it matters:** For the self-hosting crowd, this is the exact nightmare scenario. Your domains aren't just URLs; they're the front door to your Homelab services, your email, your `*.home.arpa`-adjacent DNS records, your identity. A registrar can theoretically yank all of it on a compliance flag, a fraud heuristic, or a billing dispute — and the r/selfhosted front page spent the week circling the same anxiety from a different angle: [Namecheap's price increases](https://www.reddit.com/r/selfhosted/comments/1x6oaco/namecheap_price_increases/) and threads asking for a [trustworthy EU-based registrar](https://www.reddit.com/r/selfhosted/comments/1x4fsl6/trustworthy_eu_based_domain_provider/). The lesson isn't "Namecheap is evil" — it's that your domain is a *dependency* on a single third party, and single points of failure are precisely what self-hosting is supposed to eliminate.

**The takeaway:** Register critical domains with a provider you've vetted, keep your registrar account credentials locked down, and know the appeal path *before* you need it. A domain is too important to treat as a set-and-forget purchase.

[**The r/sysadmin thread →**](https://www.reddit.com/r/sysadmin/comments/1x8cycd/namecheap_just_seized_and_disabled_all_my_domains/)

---

## 2. "Someone Behind the Software": A Defense of Human Craft

**What it is:** [Karri Saarinen](https://karrisaarinen.com/posts/someone-behind-the-software/), co-founder of Linear, wrote a short essay this week arguing that good products carry the perspective of the people who build them — their taste, their mistakes, what they choose *not* to do — and that this is exactly what the "automate the whole pipeline with agents" narrative threatens. It hit 400 points on Hacker News.

**Why it matters:** This is the natural follow-on to last week's sustainability reckoning, but from the *builder's* side rather than the *maintainer's*. Saarinen's point is that software has a character, and character comes from a human making judgment calls — not from "collect requirements, build features, measure whether they work." As agent-built software starts to flood the self-hosted ecosystem, the essay is a useful filter: the tools that feel *thoughtful* are usually the ones with a specific human's fingerprints on them. It also reframes why the community keeps gravitating to projects with a strong individual maintainer — that person *is* the product's point of view.

**The takeaway:** When you're choosing between two self-hosted tools, the one with a discernible human opinion behind it will age better than the one that feels factory-stamped. Taste is a feature.

[**Read the essay →**](https://karrisaarinen.com/posts/someone-behind-the-software/)

---

## 3. RepRapMicron: A 3D Printer That Works at Micron Scale

**What it is:** [RepRapMicron](https://github.com/VikOlliver/RepRapMicron/wiki) — a RepRap 3D printer project designed to print at the *micron* scale — topped Hacker News at 370 points. This is the homebrew end of a genuinely wild idea: a printer whose layer resolution is measured in thousandths of a millimeter.

**Why it matters:** Self-hosting and 3D printing have always shared a DNA — both are about owning your production pipeline, whether that's software or physical parts. RepRapMicron is the maker-movement spirit at its purest: an open hardware project pushing into a resolution regime that commercial machines don't touch, built by a community of tinkerers. It also connects to a thread we covered recently ([self-hosted 3D printing](/blog/2026-10-09-self-hosted-3d-printing)) — the homelab isn't just where your *services* live, it's increasingly where your *tooling* gets built too. Micron-scale printing is a long way from a Plex server, but the ethos is identical.

**The takeaway:** Even if you'll never print at micron scale, RepRapMicron is a reminder that the "self-hosted" impulse applies to hardware too — and the frontier keeps moving further from the factory.

[**RepRapMicron on GitHub →**](https://github.com/VikOlliver/RepRapMicron/wiki)

---

## 4. Dockge Goes Quiet, and the Community Migrates to Arcane

**What it is:** [Dockge](https://github.com/louislam/dockge) — the popular Docker Compose stack manager from the Uptime Kuma author, 24,000+ stars — hasn't seen a commit since April, and r/selfhosted [noticed](https://www.reddit.com/r/selfhosted/comments/1x5wv5w/apparently_dockge_is_dead_how_do_i_migrate_to/). The thread's title says it plainly: "Apparently Dockge is dead." The community's answer is [Arcane](https://github.com/getarcaneapp/arcane), a "modern Docker management" tool that's been climbing steadily.

**Why it matters:** This is the "bus factor" made practical. Dockge wasn't archived — it just *stopped*, the way single-maintainer projects do when life happens. For everyone who built their stack around it, that's a migration they didn't plan for. The thread is also a neat case study in how self-hosters self-organize: someone asks how to move their `/opt/stacks` directory over to Arcane, and the replies walk them through autodetect, stopping containers first, and the gotchas. The tooling churn is real, and it's why "don't over-customize your Docker manager" is quietly good advice.

**The takeaway:** Watch the last-commit date, not just the star count. A quiet project with one maintainer is always one life event away from becoming a migration project.

[**The migration thread →**](https://www.reddit.com/r/selfhosted/comments/1x5wv5w/apparently_dockge_is_dead_how_do_i_migrate_to/)

---

## 5. "If You Don't Run Your Own LLM Proxy, How Do You Know What's Going On?"

**What it is:** A [bluntly-titled post](https://jrdsgl.com/if-you-dont-run-your-own-llm-proxy-how-the-fuck-do-you-even-know-whats-going-on/) made the Hacker News front page arguing that as AI agents start doing real work in your stack, routing them through your own LLM proxy — not a hosted API you can't inspect — is the only way to actually see what's being sent, spent, and returned.

**Why it matters:** We've spent months covering the *what* of self-hosted AI — which models, which hardware, which UIs. This is the *observability* question catching up. When your agent fires a thousand API calls to automate a task, a hosted provider shows you a bill and a vague usage graph. Your own proxy shows you every prompt, every token, every tool call. It's the same argument people made about running their own DNS or their own reverse proxy: **you can't secure or optimize what you can't see.** The post landed right as agent workloads are shifting from toys to "things that touch your data and your money," which makes it timely rather than merely ideological.

**The takeaway:** If agents are doing real work for you, put a proxy in front of them. Observability isn't a nice-to-have once the automation starts touching things that matter.

[**Read the post →**](https://jrdsgl.com/if-you-dont-run-your-own-llm-proxy-how-the-fuck-do-you-even-know-whats-going-on/)

---

## 6. Backup Tapes Come Back to the Homelab

**What it is:** A [Hackaday piece](https://hackaday.com/2026/10/12/backup-tapes-come-back-to-the-homelab/) on setting up an LTO-5 tape drive for cold storage — 1.5 TB of uncompressed data on a palm-sized cartridge, available cheap on the used market while hard drive prices stay stubbornly high.

**Why it matters:** It's the great paradox of 2026: in the year of Ollama, *magnetic tape* is still the cheapest-per-gigabyte storage you can buy. For data hoarders — the same people running Immich, Audiobookshelf, and every other self-hosted archive — tape is the cold-storage answer that hard drives and cloud both struggle to beat on raw cost. The 3-2-1 backup rule needs an offline copy anyway, and a $50 used LTO-5 drive plus cheap cartridges is a genuinely rational choice for the "fire, theft, ransomware" copy of your media library. It's niche, yes — but it's the kind of niche the homelab community embraces with glee.

**The takeaway:** Your 3-2-1 strategy's "offline copy" doesn't have to be another hard drive. Tape is absurd, and also cheap, and also back.

[**Backup tapes on Hackaday →**](https://hackaday.com/2026/10/12/backup-tapes-come-back-to-the-homelab/)

---

## Honorable Mentions

- **SparkyFitness's dev wants people to *stop* paying him** — an [r/selfhosted thread](https://www.reddit.com/r/selfhosted/comments/1x4shcc/what_is_happening_over_at_sparkyfitness_dev_wants/) about a maintainer actively telling users to quit donating, because the money creates pressure he doesn't want. The inverse of the usual burnout story, and oddly heartwarming.
- **"Anyone else slowly moving away from complicated setups?"** — a [thread](https://www.reddit.com/r/selfhosted/comments/1x8jmu5/anyone_else_slowly_moving_away_from_complicated/) that clearly struck a nerve, with users confessing they're pruning their stacks back to a handful of services. The simplicity backlash is real.
- **Threat-hunt your selfhosted logs in 10 minutes** — a [practical guide](https://www.reddit.com/r/selfhosted/comments/1x5tes3/threathunt_your_selfhosted_logs_in_10_minutes/) to spotting suspicious activity in your own logs. Cheap security wins, always welcome.
- **TrailBase 0.34** (5,700+ stars) — a [single-executable Firebase alternative](https://github.com/trailbaseio/trailbase) in Rust/SQLite/Wasmtime, with type-safe APIs, realtime subscriptions, and an admin UI. The "Firebase but self-hosted" lane keeps maturing.
- **PS5 jailbreak gets native PS2 disc support** — a [Tom's Hardware piece](https://www.tomshardware.com/video-games/playstation/ps5-hack-delivers-native-ps2-disc-support-and-4k-upscaling-where-sony-refused-to-after-ps2-breakthrough-homebrew-dev-confirms-ps3-disc-support-is-next-for-ps5) on homebrew delivering 4K-upscaled PS2 discs where Sony refused. Same "own your hardware" spirit, different room.

---

## Closing Thought

Strip away the specifics and this week was about **taking the things you trust and auditing them.** Your registrar can seize your domains. Your Docker manager can quietly stop getting commits. Your AI agents can spend your money invisibly. Your hard drives can cost more than the tape that predates most of them. None of this is doom — it's the recurring self-hosting lesson that *ownership means vigilance*.

There's a quiet optimism underneath it, though. Saarinen's essay is a reminder that the fix for factory-stamped software is *more humans in the loop*, not fewer. RepRapMicron is a reminder that the maker impulse is alive and pushing into new regimes. And the guy whose SparkyFitness donations he's trying to refuse is proof that the people behind the stack are, against all odds, still the best part of it.

Audit your dependencies. Vouch for your maintainers. And maybe give tape a second look. What's landing in your homelab this week? Drop a comment if something caught your eye.

---

_This is a weekly series covering trending self-hosted projects, homelab tools, and open-source infrastructure. Subscribe via RSS or follow devhandbook.io for more._
