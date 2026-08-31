---
layout: post.njk
title: "Claude Code Is Leaking Your Session URLs"
date: 2026-08-31
description: "Claude Code auto-appends your session URL to commit messages and PR descriptions — and that URL can expose your full conversation, including secrets, to anyone who can read your git history. Here's how the leak works, how to reproduce it, and a git-history scanner to find every URL you've already leaked."
tags: ["claude-code", "security", "privacy", "data-leak", "ai-coding", "git", "scanner", "secrets", "anthropic", "developer-tools"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-31-claude-code-session-url-leak"
---

A Hacker News thread titled **"Claude Code Is Leaking Your Session URLs"** hit 189 points this week, and the reaction was a mix of "wait, what?" and "oh no, I've been doing this for months."

The short version: Claude Code, Anthropic's terminal coding agent, has a habit of **auto-appending your session URL to commit messages and pull-request descriptions.** That URL points back to your full Claude conversation — the entire transcript, including every file it read, every command it ran, and every secret that happened to scroll past.

If you've been committing Claude Code's suggested messages without reading them closely, there's a decent chance your git history is now a public index of your AI sessions. This post explains exactly how the leak works, how to reproduce it on your own machine, and — because I don't like writing about a problem without shipping a fix — a scanner you can run against any repo to find every session URL you've already leaked.

## The Leak, in One Paragraph

Claude Code is designed to be helpful, and one of the ways it's helpful is by writing your commit messages and PR descriptions for you. The problem is that it *also* appends a line like this to the end of them:

```
🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

That part is fine. But in many configurations — and especially when you use the `/commit` or PR-generation features — it also drops in a link to the *session itself*:

```
Session: https://claude.ai/share/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

That URL is a shareable link to your conversation. Depending on your settings, it can be **publicly accessible to anyone with the link.** And the link is now baked into your commit message, which means it's in your git history, which means it's in your remote, which means it's in every clone, fork, and mirror of your repo — forever.

The HN thread's core complaint is that this happens **silently.** You ask Claude Code to commit, it writes a nice message, you glance at the first line, you hit enter. You never notice the URL at the bottom. And now your entire session — including any API keys, database credentials, or internal architecture you pasted into the chat — is one link away from anyone who can read your commit log.

## Why This Is Worse Than a Normal Secret Leak

A leaked API key is bad, but it's *contained.* You rotate the key, you're done. A leaked session URL is different in three ways:

**1. It's a link to *everything*, not one thing.** A single session can contain dozens of secrets, internal URLs, customer data, and architectural decisions. One URL leaks all of it at once.

**2. It's not greppable by normal secret scanners.** Tools like `gitleaks` and `trufflehog` look for high-entropy strings and known key patterns. A `claude.ai/share/` URL doesn't match any of those patterns, so it sails right past your CI secret-scanning. You can have a fully "clean" secret scan and still be leaking your entire session history.

**3. It's in your *history*, not your working tree.** Even if you catch it and amend the commit, the original commit object still exists in your reflog, in any forks, and in any clone that pulled before you fixed it. Git history is append-only in practice. Once it's pushed, assume it's permanent.

This is the part that makes it a genuine footgun rather than a minor annoyance: **the leak is invisible to the tools you already trust to catch leaks.**

## Reproduce It Yourself (5 Minutes)

Don't take my word for it. Here's how to see the behavior on your own machine:

```bash
# 1. Make a throwaway repo
mkdir /tmp/claude-leak-test && cd /tmp/claude-leak-test
git init
echo "hello" > README.md
git add README.md

# 2. Start Claude Code and make a trivial change
claude
#   > "Add a comment to README.md"
#   > /commit

# 3. Inspect the commit message it generated
git log -1 --format=%B
```

Look at the *full* message, not just the first line. If you see a `claude.ai/share/` or `claude.ai/chat/` URL in there, you've reproduced it.

The exact behavior varies by version and by whether you've enabled session sharing, but the pattern is consistent: **Claude Code treats your session URL as a useful artifact to attach to your work product, and it doesn't ask before doing so.** The default posture is "share," not "ask."

## The Scanner: Find Every URL You've Already Leaked

The fix has two halves: stop the leak going forward, and find what's already out there. The second half is the one nobody talks about, so here's a scanner.

Save this as `scan-claude-leaks.sh` and run it from the root of any repo:

```bash
#!/usr/bin/env bash
# scan-claude-leaks.sh — find Claude Code session URLs in git history
set -euo pipefail

# Patterns that match Claude session/share URLs
PATTERN='claude\.ai/(share|chat|code)/[A-Za-z0-9_-]{8,}'

echo "Scanning git history for Claude session URLs..."
echo "Repo: $(git rev-parse --show-toplevel 2>/dev/null || pwd)"
echo

# Walk every commit, every branch, every tag
git rev-list --all | while read -r commit; do
  # Check the commit message
  msg=$(git log -1 --format=%B "$commit" 2>/dev/null || true)
  if echo "$msg" | grep -Eiq "$PATTERN"; then
    url=$(echo "$msg" | grep -Eio "$PATTERN" | head -1)
    short=$(git log -1 --format=%h "$commit")
    echo "⚠️  COMMIT MESSAGE  $short  $url"
  fi

  # Check the diff for the URL appearing in added lines
  git show --format= --no-ext-diff "$commit" 2>/dev/null \
    | grep -E "^\+" \
    | grep -Eio "$PATTERN" \
    | sort -u \
    | while read -r url; do
        short=$(git log -1 --format=%h "$commit")
        echo "⚠️  DIFF CONTENT    $short  $url"
      done
done

echo
echo "Done. Any lines above starting with ⚠️ are leaked session URLs."
echo "For each one: (1) revoke/disable the share link, (2) rotate any secrets"
echo "that appeared in that session, (3) rewrite history if the repo is private."
```

Run it:

```bash
chmod +x scan-claude-leaks.sh
./scan-claude-leaks.sh
```

The scanner checks two places: the **commit message** (where Claude Code appends the URL) and the **diff content** (where a URL might have been pasted into a file, a README, or a changelog). Both are in your permanent history, and both are invisible to standard secret scanners.

If you want to scan *all* your repos at once, wrap it in a loop:

```bash
for repo in ~/Projects/*/.git; do
  (cd "$(dirname "$repo")" && ./scan-claude-leaks.sh)
done
```

## How to Stop the Leak Going Forward

The scanner finds what's already leaked. Here's how to stop adding to it:

**1. Read the full commit message before you accept it.** This sounds obvious, but the whole problem is that the URL is at the *bottom*, below the fold of your attention. Train yourself to scroll to the end of every Claude-generated commit message.

**2. Disable session sharing.** In Claude Code's settings, turn off the option that makes sessions shareable. If the session can't be shared, the URL is useless even if it leaks. This is the single highest-leverage fix.

**3. Strip the URL automatically.** Add a `prepare-commit-msg` hook that removes any `claude.ai/` URL before the message is committed:

```bash
#!/usr/bin/env bash
# .git/hooks/prepare-commit-msg — strip Claude session URLs
sed -i '' -E 's#https?://claude\.ai/(share|chat|code)/[A-Za-z0-9_-]+##g' "$1"
```

**4. Add the pattern to your CI secret scanner.** If you use `gitleaks`, add a custom rule for `claude.ai/(share|chat|code)/`. It won't catch what's already in history, but it'll block new leaks at the PR stage.

**5. Treat every session as if it's public.** The uncomfortable truth is that you can't fully control what an agent does with your conversation. Don't paste secrets into Claude Code sessions that you wouldn't be okay with leaking. Use environment variables and secret managers, and reference them by name, not by value.

## The Bigger Pattern

This isn't really about Claude Code. It's about a category of leak that's going to keep happening as AI agents get more autonomous.

The pattern is: **an agent produces an artifact (a commit, a PR, a doc) and attaches a reference to its own context as a convenience feature — without realizing that the reference is a data-exfiltration vector.** The agent is trying to be helpful. The URL is genuinely useful for *you* to jump back into the session. But "useful for you" and "safe to publish" are two different things, and the agent doesn't know the difference.

We saw the same shape with the [MCP servers attack surface](/blog/2026-08-16-mcp-servers-attack-surface/) — a convenience feature that became an attack vector because nobody thought about the security implications until it was too late. And with the [AI code review gap](/blog/2026-08-18-ai-code-review-checklist/) — the assumption that AI output is finished work, when it actually needs *more* scrutiny than a first draft.

The common thread: **we're wiring agents into our workflows faster than we're building the guardrails around them.** The session-URL leak is a small, concrete example of a much larger problem. The fix isn't to stop using the tools. It's to build the review layer — the scanner, the hook, the habit of reading the full message — that catches the leaks before they become permanent.

## The Bottom Line

Claude Code is appending your session URL to your commits and PRs, and that URL can expose your entire conversation to anyone who can read your git history. It's invisible to standard secret scanners, it's permanent once pushed, and it's been happening silently for months.

Here's the card to stick on your monitor:

1. **Read the full commit message — the URL is at the bottom.**
2. **Disable session sharing in Claude Code.**
3. **Run the scanner above against every repo you've touched.**
4. **Add a `prepare-commit-msg` hook to strip `claude.ai/` URLs.**
5. **Treat every agent session as if it's public.**

The leak is real, it's reproducible, and it's probably already in your history. The good news is that it's also fixable — if you go looking for it.

---

*Have you found a `claude.ai/share/` URL in your own git history? Run the scanner and let me know what you find — I'm on [GitHub](https://github.com/bryanmoon19) or in the comments below.*

*If you found this useful, you might also like my posts on the [MCP servers attack surface](/blog/2026-08-16-mcp-servers-attack-surface/), the [AI code review checklist](/blog/2026-08-18-ai-code-review-checklist/), and [de-risking your AI coding setup after the Cursor/SpaceX news](/blog/2026-08-30-cursor-spacex-alternatives-migration-guide/).*
