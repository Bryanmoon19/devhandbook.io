#!/usr/bin/env python3
"""
Self-Hosted Weekly Roundup Generator
Scrapes r/selfhosted, r/homelab, and Hacker News for trending topics
and generates a formatted devhandbook.io blog post draft.

Usage:
    python3 scripts/weekly-roundup-generator.py [--date YYYY-MM-DD]

Output:
    blog/drafts/selfhosted-weekly-YYYY-MM-DD.md
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from html import unescape
from typing import List, Dict, Optional

# Configuration
REDDIT_USER_AGENT = "devhandbook-weekly-bot/1.0 (by /u/bryanmoon)"
SUBREDDITS = ["selfhosted", "homelab"]
HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"

# Keywords to filter for self-hosted / homelab relevance
RELEVANT_KEYWORDS = [
    "self-host", "self host", "selfhost", "homelab", "home lab",
    "docker", "kubernetes", "k8s", "proxmox", "lxc",
    "nas", "nextcloud", "plex", "jellyfin", "immich",
    "home assistant", "homeassistant", "automation",
    "wireguard", "vpn", "pi-hole", "pihole",
    "open source", "github", "gitlab",
    "server", "raspberry pi", "rpi", "arm",
    "backup", "zfs", "raid", "storage",
    "monitoring", "prometheus", "grafana",
    "ai", "llm", "local ai", "ollama",
]

SELF_HOSTED_KEYWORDS = [
    "self-host", "self host", "selfhost", "homelab", "home lab",
    "docker", "kubernetes", "proxmox", "nextcloud", "plex",
    "jellyfin", "immich", "home assistant", "wireguard",
    "pi-hole", "pihole", "raspberry pi",
]


def fetch_json(url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
    """Fetch JSON from a URL with error handling."""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def is_relevant_post(title: str, text: str = "") -> bool:
    """Check if a post is relevant to self-hosting/homelab."""
    combined = f"{title} {text}".lower()
    return any(kw.lower() in combined for kw in RELEVANT_KEYWORDS)


def score_relevance(title: str, text: str = "", score: int = 0, comments: int = 0) -> float:
    """Score how relevant and high-quality a post is."""
    combined = f"{title} {text}".lower()
    relevance_score = 0.0
    
    # Base score from upvotes
    if score > 0:
        relevance_score += min(score / 100, 10)  # Cap at 10
    
    # Bonus for engagement
    if comments > 10:
        relevance_score += min(comments / 50, 5)
    
    # Keyword matching bonus
    for kw in SELF_HOSTED_KEYWORDS:
        if kw.lower() in combined:
            relevance_score += 2
    
    # Penalize very short or vague titles
    if len(title) < 30:
        relevance_score *= 0.7
    
    return relevance_score


def fetch_reddit_posts(subreddit: str, limit: int = 50) -> List[Dict]:
    """Fetch top posts from a subreddit for the past week."""
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=week&limit={limit}"
    headers = {"User-Agent": REDDIT_USER_AGENT}
    
    data = fetch_json(url, headers)
    if not data or "data" not in data:
        return []
    
    posts = []
    for child in data["data"].get("children", []):
        post = child.get("data", {})
        if not post:
            continue
            
        posts.append({
            "title": unescape(post.get("title", "")),
            "url": post.get("url", ""),
            "permalink": f"https://reddit.com{post.get('permalink', '')}",
            "score": post.get("score", 0),
            "comments": post.get("num_comments", 0),
            "subreddit": post.get("subreddit", ""),
            "selftext": post.get("selftext", ""),
            "created_utc": post.get("created_utc", 0),
            "author": post.get("author", "[deleted]"),
        })
    
    return posts


def fetch_hn_relevant_stories(limit: int = 100) -> List[Dict]:
    """Fetch top HN stories and filter for self-hosted relevance."""
    # Get top story IDs
    top_ids = fetch_json(HN_TOP_STORIES_URL)
    if not top_ids:
        return []
    
    stories = []
    for story_id in top_ids[:limit]:
        story = fetch_json(HN_ITEM_URL.format(story_id))
        if not story:
            continue
        
        title = story.get("title", "")
        url = story.get("url", "")
        text = story.get("text", "")
        
        if is_relevant_post(title, text):
            stories.append({
                "title": unescape(title),
                "url": url or f"https://news.ycombinator.com/item?id={story_id}",
                "score": story.get("score", 0),
                "comments": story.get("descendants", 0),
                "source": "Hacker News",
                "time": story.get("time", 0),
            })
    
    return stories


def fetch_hn_search(query: str = "self-hosted", limit: int = 20) -> List[Dict]:
    """Search HN Algolia API for specific topics."""
    url = f"{HN_SEARCH_URL}?query={urllib.parse.quote(query)}&tags=story&hitsPerPage={limit}"
    data = fetch_json(url)
    
    if not data or "hits" not in data:
        return []
    
    stories = []
    for hit in data["hits"]:
        stories.append({
            "title": unescape(hit.get("title", "")),
            "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
            "score": hit.get("points", 0),
            "comments": hit.get("num_comments", 0),
            "source": "Hacker News",
            "time": hit.get("created_at_i", 0),
        })
    
    return stories


def deduplicate_posts(posts: List[Dict]) -> List[Dict]:
    """Remove duplicate posts based on URL or title similarity."""
    seen_urls = set()
    seen_titles = set()
    unique = []
    
    for post in posts:
        url = post.get("url", "").rstrip("/")
        title = post.get("title", "").lower()
        
        # Skip if exact URL match
        if url and url in seen_urls:
            continue
        
        # Skip if very similar title (fuzzy match)
        title_normalized = re.sub(r'[^\w\s]', '', title).strip()
        if title_normalized in seen_titles:
            continue
        
        seen_urls.add(url)
        seen_titles.add(title_normalized)
        unique.append(post)
    
    return unique


def categorize_post(post: Dict) -> str:
    """Categorize a post into a section."""
    title = post.get("title", "").lower()
    text = post.get("selftext", "").lower()
    combined = f"{title} {text}"
    
    categories = {
        "🚀 New Releases & Updates": [
            "release", "update", "new version", "announce", "launch",
            "just released", "v0.", "v1.", "version ", "changelog",
        ],
        "📊 Show & Tell": [
            "show hn", "show /r", "my setup", "my homelab", "my selfhosted",
            "built", "i made", "i created", "showoff", "showcase",
        ],
        "💡 Guides & Tutorials": [
            "guide", "tutorial", "how to", "howto", "getting started",
            "beginner", "step by step", "walkthrough", "explained",
        ],
        "🛠️ Tools & Projects": [
            "tool", "project", "open source", "github", "self-hosted",
            "alternative to", "replacement for", "vs ", "versus",
        ],
        "🔒 Security & Privacy": [
            "security", "privacy", "vpn", "wireguard", "encrypt",
            "auth", "2fa", "mfa", "breach", "vulnerability",
        ],
        "🤖 AI & Automation": [
            "ai", "llm", "local ai", "ollama", "automation",
            "agent", "bot", "machine learning", "ml ", "openai",
        ],
    }
    
    for category, keywords in categories.items():
        if any(kw in combined for kw in keywords):
            return category
    
    return "📰 Community Highlights"


def generate_roundup_content(posts: List[Dict], week_of: str) -> str:
    """Generate the weekly roundup blog post content."""
    
    # Categorize posts
    categorized = {}
    for post in posts:
        cat = categorize_post(post)
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(post)
    
    # Build content
    lines = [
        "---",
        "layout: post.njk",
        f'title: "Self-Hosted This Week: {week_of}"',
        f'date: {week_of}',
        f'description: "The best self-hosted tools, guides, and community highlights from the week of {week_of}."',
        'tags: ["self-hosted", "homelab", "roundup", "weekly", "docker", "open-source"]',
        'author: "Bryan Moon"',
        f'canonical: "https://devhandbook.io/blog/selfhosted-weekly-{week_of}"',
        "---",
        "",
        f"# Self-Hosted This Week: {week_of}",
        "",
        f"Welcome to the weekly roundup for {week_of}. Here's what caught my attention in the self-hosting and homelab communities this week.",
        "",
        "---",
        "",
    ]
    
    # Add categorized sections
    category_order = [
        "🚀 New Releases & Updates",
        "🤖 AI & Automation",
        "🛠️ Tools & Projects",
        "💡 Guides & Tutorials",
        "📊 Show & Tell",
        "🔒 Security & Privacy",
        "📰 Community Highlights",
    ]
    
    for category in category_order:
        if category not in categorized or not categorized[category]:
            continue
        
        lines.extend([
            f"## {category}",
            "",
        ])
        
        for post in categorized[category][:5]:  # Max 5 per category
            title = post.get("title", "Untitled")
            url = post.get("url", "")
            source = post.get("subreddit", post.get("source", ""))
            score = post.get("score", 0)
            comments = post.get("comments", 0)
            
            # Format line
            lines.append(f'### [{title}]({url})')
            lines.append("")
            
            # Add metadata line
            meta_parts = []
            if source:
                meta_parts.append(f"via {source}")
            if score:
                meta_parts.append(f"{score} upvotes")
            if comments:
                meta_parts.append(f"{comments} comments")
            
            if meta_parts:
                lines.append(f"*{', '.join(meta_parts)}*")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Add footer
    lines.extend([
        "## See Something I Missed?",
        "",
        "Drop it in the comments or [reach out on Telegram](https://t.me/bmoon19). I read everything.",
        "",
        "---",
        "",
        "*This post is auto-generated from community submissions across Reddit and Hacker News, then curated and edited by hand. Want to submit something for next week's roundup? [Send it my way](https://t.me/bmoon19).*",
        "",
    ])
    
    return "\n".join(lines)


def generate_week_label(date: datetime) -> str:
    """Generate a human-readable week label."""
    # Get the Monday of this week
    monday = date - timedelta(days=date.weekday())
    sunday = monday + timedelta(days=6)
    
    if monday.month == sunday.month:
        return f"{monday.strftime('%B %d')}–{sunday.strftime('%d, %Y')}"
    else:
        return f"{monday.strftime('%B %d')}–{sunday.strftime('%B %d, %Y')}"


def main():
    parser = argparse.ArgumentParser(description="Generate self-hosted weekly roundup")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--output-dir", help="Output directory", default="blog")
    parser.add_argument("--limit", help="Max posts per source", type=int, default=50)
    args = parser.parse_args()
    
    # Determine target date
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        target_date = datetime.now()
    
    week_of = generate_week_label(target_date)
    date_str = target_date.strftime("%Y-%m-%d")
    
    print(f"📅 Generating weekly roundup for week of {week_of}")
    print(f"📝 Output will be saved to: blog/selfhosted-weekly-{date_str}.md")
    print()
    
    # Fetch posts from all sources
    all_posts = []
    
    print("🔍 Fetching from Reddit...")
    for subreddit in SUBREDDITS:
        print(f"  r/{subreddit}...", end=" ", flush=True)
        posts = fetch_reddit_posts(subreddit, limit=args.limit)
        print(f"{len(posts)} posts")
        all_posts.extend(posts)
    
    print("🔍 Fetching from Hacker News...", end=" ", flush=True)
    hn_posts = fetch_hn_relevant_stories(limit=args.limit)
    print(f"{len(hn_posts)} posts")
    all_posts.extend(hn_posts)
    
    print(f"\n📊 Total raw posts: {len(all_posts)}")
    
    # Score and filter
    print("\n🎯 Scoring relevance...")
    scored_posts = []
    for post in all_posts:
        score = score_relevance(
            post.get("title", ""),
            post.get("selftext", ""),
            post.get("score", 0),
            post.get("comments", 0)
        )
        if score > 3:  # Minimum relevance threshold
            post["_relevance_score"] = score
            scored_posts.append(post)
    
    # Sort by relevance score
    scored_posts.sort(key=lambda x: x["_relevance_score"], reverse=True)
    
    # Deduplicate
    print("🧹 Deduplicating...")
    unique_posts = deduplicate_posts(scored_posts)
    print(f"📊 Unique relevant posts: {len(unique_posts)}")
    
    if len(unique_posts) < 5:
        print("⚠️ Warning: Very few relevant posts found. Results may be thin.", file=sys.stderr)
    
    # Take top posts
    top_posts = unique_posts[:25]
    
    # Generate content
    print("✍️  Generating blog post...")
    content = generate_roundup_content(top_posts, week_of)
    
    # Write output
    output_path = f"blog/selfhosted-weekly-{date_str}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\n✅ Done! Saved to: {output_path}")
    print(f"   {len(top_posts)} posts included")
    print(f"   {len(categorize_post.__code__.co_consts)} categories used")
    
    # Print summary
    print("\n📋 Post Summary:")
    categorized = {}
    for post in top_posts:
        cat = categorize_post(post)
        if cat not in categorized:
            categorized[cat] = 0
        categorized[cat] += 1
    
    for cat, count in sorted(categorized.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count} posts")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Review: cat {output_path}")
    print(f"   2. Edit as needed")
    print(f"   3. git add . && git commit -m \"Add weekly roundup: {week_of}\"")
    print(f"   4. Post-commit hook will auto-deploy!")


if __name__ == "__main__":
    main()
