---
layout: post.njk
title: "Postgres for Everything: Replace Redis, Cron, Queues, and Search with One Database (Homelab Edition)"
date: 2026-08-20
description: "The 'PostgreSQL for Everything' wave keeps hitting the Hacker News front page, and for good reason — Postgres can now do caching, job scheduling, message queues, and full-text search. But the people who benefit most aren't startups. They're homelabbers running five separate services on a Mac mini or a single LXC. Here's how to collapse Redis, cron, a queue, and a search engine into one Postgres instance, and when you shouldn't."
tags: ["postgres", "postgresql", "homelab", "redis", "cron", "queues", "search", "self-hosted", "database", "lxc", "proxmox", "resource-consolidation", "pgbouncer", "pg_cron", "pgvector"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-20-postgres-for-everything-homelab"
---

There's a recurring wave on Hacker News that never quite dies. It goes by a few names — **"PostgreSQL for Everything,"** **"Just Use Postgres,"** **"You Don't Need Redis"** — and it resurfaces every few months with a fresh batch of extensions and a fresh round of "well, actually" in the comments.

This week's version hit 325 points, and the thesis is the same as it's always been: Postgres has quietly absorbed the jobs you used to need four or five separate services for. Caching? There's an extension for that. Job scheduling? `pg_cron`. Message queues? `pgmq` or `SKIP LOCKED`. Full-text search? Built in, and good enough for most people. Vector search? `pgvector`.

The startup crowd argues about this endlessly, because at their scale the tradeoffs are real and the "one database" answer is genuinely wrong for some workloads. But there's a group that benefits from this idea far more than any startup, and they're almost never the ones in the HN thread:

**Homelabbers.**

If you're running a Mac mini or a single Proxmox LXC, you're not choosing between Postgres and a dedicated Redis cluster. You're choosing between *one* Postgres container and *five* containers — Redis, a cron daemon, a queue worker, a search engine, and Postgres itself — all fighting over 4GB of RAM and two cores. The "Postgres for Everything" pitch isn't a scalability argument for you. It's a **resource-consolidation argument.**

This post is the homelab edition of that wave. What you can actually collapse into Postgres, what you shouldn't, and the exact extensions and SQL to do it.

## The Five Services You're Probably Running (That Postgres Can Replace)

Let me be concrete about the stack I'm talking about, because it's the stack most self-hosters end up with by accident. You start with one app that needs a database, so you spin up Postgres. Then the next app needs a cache, so you add Redis. Then you need a scheduled job, so you bolt on a cron container or a scheduler. Then something needs a background queue, so you add a queue broker. Then you want search, so you add Meilisearch or Typesense or Elasticsearch.

Before you know it, you've got five stateful services running on a box that was supposed to be "just a little homelab." Each one is a container with its own memory overhead, its own backup story, its own update cadence, and its own way of silently breaking.

Here's the thing: **Postgres can do all five of those jobs.** Not perfectly, and not at every scale — but at homelab scale, "good enough" is the entire game. Let me walk through each one.

### 1. Caching (Replace Redis)

The most common objection to "Postgres for Everything" is caching. "You can't use Postgres as a cache, it's too slow, Redis is in-memory." And that's true if you're doing 50,000 reads per second. You are not doing 50,000 reads per second on a Mac mini.

For homelab workloads, the right tool is **`UNLOGGED` tables.** An unlogged table skips the write-ahead log, which means writes are dramatically faster and the table lives mostly in shared buffers (Postgres's in-memory cache). The tradeoff is that an unlogged table is truncated on crash — which is *exactly* what you want from a cache anyway. A cache that survives a crash is just a second database.

```sql
CREATE UNLOGGED TABLE cache (
    key   text PRIMARY KEY,
    value jsonb NOT NULL,
    expires_at timestamptz NOT NULL
);

-- Read with automatic expiry
SELECT value FROM cache
WHERE key = $1 AND expires_at > now();

-- Write with a TTL
INSERT INTO cache (key, value, expires_at)
VALUES ($1, $2, now() + interval '5 minutes')
ON CONFLICT (key) DO UPDATE
SET value = EXCLUDED.value, expires_at = EXCLUDED.expires_at;
```

Add a `pg_cron` job to sweep expired rows once a minute and you've got a cache with TTLs, eviction, and zero extra infrastructure. If you want to get fancy, there's also the `pgmemcache` extension, but for most homelab apps the unlogged-table pattern is all you need.

The honest caveat: if you're running something like [Immich](/blog/2026-06-17-immich-photo-management-homelab/) or a busy [Jellyfin](/blog/2026-08-10-jellyfin-ecosystem-stack/) instance that *expects* a Redis-compatible cache, don't rip Redis out just to prove a point. But for your own apps and scripts, Postgres-as-cache removes a whole service.

### 2. Job Scheduling (Replace Cron)

`pg_cron` is the extension that makes this one a no-brainer. It runs a cron daemon *inside* Postgres, so your scheduled jobs live in the database next to the data they operate on. No separate cron container, no `crontab -e` on a host you'll forget you edited, no "which box is this job actually running on" mystery.

```sql
CREATE EXTENSION pg_cron;

-- Run a cleanup job every night at 3am
SELECT cron.schedule('nightly-cleanup', '0 3 * * *',
  $$DELETE FROM cache WHERE expires_at < now()$$);

-- Run a job every 5 minutes
SELECT cron.schedule('process-queue', '*/5 * * * *',
  $$SELECT process_pending_jobs()$$);
```

The killer feature for homelabbers is that `pg_cron` jobs are **backed up with your database.** Your cron schedule isn't a file on a host that might get wiped; it's rows in a table that get captured by your existing Postgres backup. If you've read our [Docker backup playbook](/blog/2026-08-14-docker-backup-playbook-restic-dockstash/), you know how much of a pain it is to remember to back up cron state separately. `pg_cron` makes it automatic.

### 3. Message Queues (Replace Redis/RabbitMQ)

This is the one that surprises people, because "Postgres as a queue" used to be a punchline. The old advice was that using a table as a queue caused table bloat and lock contention. That advice is about a decade out of date.

The modern pattern is **`FOR UPDATE SKIP LOCKED`**, which lets multiple workers claim rows from a queue table without blocking each other. It's the same technique that powers `pgmq` (a Postgres-native queue extension) and it's rock solid at homelab throughput.

```sql
-- The queue table
CREATE TABLE jobs (
    id bigserial PRIMARY KEY,
    payload jsonb NOT NULL,
    status text NOT NULL DEFAULT 'pending',
    created_at timestamptz NOT NULL DEFAULT now()
);

-- A worker claims the next job without blocking other workers
WITH next_job AS (
    SELECT id FROM jobs
    WHERE status = 'pending'
    ORDER BY id
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE jobs SET status = 'processing'
WHERE id IN (SELECT id FROM next_job)
RETURNING id, payload;
```

If you want a more batteries-included experience, `pgmq` gives you a proper queue API (`send`, `read`, `archive`, `delete`) on top of exactly this mechanism. But the raw SQL above is genuinely enough for most homelab background work — image processing, notification dispatch, feed polling.

The caveat is throughput. If you're pushing tens of thousands of messages per second, Postgres-as-queue will eventually become your bottleneck, and you'll want a real broker. At homelab scale, you'll hit that limit approximately never.

### 4. Full-Text Search (Replace Meilisearch/Typesense/Elasticsearch)

Postgres has had full-text search built in since 2008, and it's better than most people assume. It's not as good as a dedicated engine for fuzzy matching, typo tolerance, or relevance tuning — but for "search my notes" or "search my blog posts" or "search my media library," it's more than enough.

```sql
-- Add a search vector column
ALTER TABLE posts
ADD COLUMN search tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', title), 'A') ||
    setweight(to_tsvector('english', body), 'B')
) STORED;

CREATE INDEX posts_search_idx ON posts USING GIN (search);

-- Search with ranking
SELECT title, ts_rank(search, query) AS rank
FROM posts, to_tsquery('english', 'postgres & queue') query
WHERE search @@ query
ORDER BY rank DESC
LIMIT 20;
```

The generated-column trick means the search index updates automatically whenever the row changes — no separate indexing pipeline, no "why is my search stale" debugging. For a homelab wiki, a notes app, or a personal search over your own content, this is the entire feature set you need.

Where it falls short: if you need typo-tolerant search ("postgrs" should find "postgres"), or faceted search with instant filtering, a dedicated engine like Meilisearch is still the better tool. But that's a *feature* decision, not a default. Most homelab search needs are simple keyword search, and Postgres does that natively.

### 5. Vector Search (Replace a Dedicated Vector DB)

This one's a bonus, but it's increasingly relevant given how much of the homelab world is now running [local LLMs](/blog/2026-06-12-local-llms-mac-mini-practical-guide/) and [AI agents](/blog/2026-07-29-ai-agent-sandboxes-homelab/). If you're doing RAG (retrieval-augmented generation) against your own documents, you need vector search — and `pgvector` gives it to you inside the same Postgres you already run.

```sql
CREATE EXTENSION vector;

CREATE TABLE embeddings (
    id bigserial PRIMARY KEY,
    content text NOT NULL,
    embedding vector(1536) NOT NULL
);

CREATE INDEX ON embeddings
USING hnsw (embedding vector_cosine_ops);

-- Find the 5 most similar documents
SELECT content, 1 - (embedding <=> $1) AS similarity
FROM embeddings
ORDER BY embedding <=> $1
LIMIT 5;
```

`pgvector` supports HNSW and IVFFlat indexes, cosine and L2 distance, and it's fast enough for homelab-scale RAG. You don't need Pinecone, Weaviate, or Qdrant running as a separate service. Your embeddings live next to your data, in the same backup, in the same transaction.

## The Real Win: One Backup, One Restore, One Thing to Watch

The individual feature replacements are nice, but they're not the actual argument. The actual argument is **operational simplicity.**

When you collapse five services into one, you collapse five backup jobs into one. Five restore procedures into one. Five update schedules into one. Five sets of "why is this container restarting" logs into one. On a homelab, where *you* are the entire ops team and you're doing this at 11pm on a Tuesday, that's not a minor convenience. It's the difference between a stack you can actually maintain and a stack that slowly rots because you can't keep up with all of it.

This is the same logic we've applied elsewhere on this site — the [database management playbook](/blog/2026-06-20-database-management-playbook-homelab/) and the [monitoring patterns](/blog/2026-06-21-advanced-monitoring-patterns-homelab/) posts are both, at their core, about reducing the number of things you have to babysit. "Postgres for Everything" is the most aggressive version of that philosophy, and for a resource-constrained homelab it's often the right one.

## What You Should NOT Collapse Into Postgres

I want to be honest about the limits, because the HN thread's biggest sin is overclaiming. Here's what you should keep separate, even at homelab scale:

**Redis, if an app hard-requires it.** Some self-hosted apps (Immich, certain Nextcloud configs, some Jellyfin plugins) expect a Redis-compatible server and won't work without one. Don't fight the app. Run Redis for the apps that need it, and use Postgres-as-cache for the things *you* build.

**Anything with genuinely high write throughput.** If you're ingesting thousands of events per second — high-frequency sensor data, busy log pipelines — a dedicated queue or time-series store is the right call. Postgres can do a lot, but it's not a time-series database, and pretending otherwise will hurt you.

**Search with heavy typo tolerance or faceting.** As I said above, if you need "did you mean" suggestions or instant faceted filtering, Meilisearch or Typesense earns its keep. Postgres full-text search is for keyword search, not search-engine-grade relevance.

**Anything that needs to survive a Postgres outage independently.** This is the subtle one. If you collapse your queue *and* your cache *and* your scheduler into Postgres, then a Postgres outage takes down all of them at once. For a homelab, that's usually fine — one thing to restart, one thing to restore. But if you have a service that *must* keep running even when the database is down, give it its own store.

The rule of thumb: **collapse what you can, keep what an app demands, and don't collapse your single point of failure into a bigger single point of failure without understanding the tradeoff.**

## A Concrete Homelab Setup

Here's what this looks like in practice. A single Postgres 17 container (or a Postgres install on your LXC) with the extensions enabled, replacing what used to be five containers:

```yaml
# docker-compose.yml — one container instead of five
services:
  postgres:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    # pg_cron needs to be loaded at startup
    command: >
      postgres
      -c shared_preload_libraries=pg_cron
      -c cron.database_name=app
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

Then, inside the database, enable the extensions once:

```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- fuzzy-ish text matching
CREATE EXTENSION IF NOT EXISTS vector;    -- pgvector, for RAG
-- pgmq if you want the queue API (install separately)
```

That's it. One container, one volume to back up, one set of credentials, one thing to monitor. The Redis container, the cron container, the queue broker, and the search engine are all gone.

If you're on Proxmox, this is even more compelling — a single LXC running Postgres can replace a handful of LXC containers, each of which carries its own overhead. We've written about [Proxmox LXC consolidation](/blog/2026-06-03-portainer-alternatives-proxmox-lxc/) before, and this is the database-flavored version of the same idea.

## The Bottom Line

The "PostgreSQL for Everything" wave is right more often than the HN commenters want to admit — but not for the reasons they argue about. The startup debate is about whether Postgres can *scale* to replace Redis and Kafka and Elasticsearch. The homelab answer is simpler and more boring:

**At homelab scale, Postgres can replace Redis, cron, a queue, and a search engine, and the thing you gain isn't performance — it's one backup, one restore, and one less thing to babysit.**

That's the whole pitch. If you're running five stateful services on a Mac mini or a single LXC, take a hard look at whether four of them are just Postgres wearing a different hat. Chances are, they are.

---

*Want more homelab consolidation ideas? Check out our [database management playbook](/blog/2026-06-20-database-management-playbook-homelab/) and the [midyear homelab review](/blog/2026-07-01-midyear-homelab-review-2026/).*
