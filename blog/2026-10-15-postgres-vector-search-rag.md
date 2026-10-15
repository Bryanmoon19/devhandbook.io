---
layout: post.njk
title: "You Already Run Postgres — Stop Installing a Separate Vector Database for RAG"
date: 2026-10-15
description: "The self-hosted RAG stack used to mean bolting Pinecone, Qdrant, or Weaviate onto the Postgres you already run. It doesn't anymore. pgvector plus the new Timescale pg_vectorsearch index make Postgres genuinely competitive for vector search — and a new index type just shipped that's faster than both IVFFlat and HNSW. Here's how to bolt RAG onto the database you already have, what the new index changes, and the honest limits that still send you to a dedicated vector DB."
tags: ["postgres", "postgresql", "pgvector", "pg_vectorsearch", "timescale", "rag", "vector-search", "embedding", "local-llm", "ollama", "self-hosted", "homelab", "ai", "pinecone", "qdrant", "weaviate"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-15-postgres-vector-search-rag/"
affiliate: false
cta: true
---

Here's the question I keep seeing, verbatim, on r/selfhosted and r/LocalLLaMA at least once a week:

> "I want to do RAG on my own docs. I already run Postgres for everything else. Do I need to spin up Pinecone / Qdrant / Weaviate too?"

The answer, for most of you, is **no.** And it's gotten more confidently "no" in the last few weeks, because a new vector index just landed that closes the biggest remaining gap.

I run [local LLMs on a Mac mini](/blog/2026-10-09-local-llms-mac-mini/) and I run [Postgres for everything](/blog/2026-08-20-postgres-for-everything-homelab/) — Redis, cron, queues, search, all collapsed into one instance. For a long time the one thing I *didn't* ask Postgres to do was vector search, because the honest word was that pgvector's indexes were fine for a few hundred thousand rows and then fell off a cliff compared to a dedicated engine.

That word is now out of date. Here's what changed, how to set it up, and — because I refuse to write a "vector database comparison" listicle that ignores the tradeoffs — the decision tree for when Postgres stops being enough.

---

## The Setup You Already Know

If you've been around pgvector at all, none of this is new. You enable the extension, add a vector column, and query with cosine distance:

```sql
-- once per database
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    content     text,
    embedding   vector(768)   -- dims match your embedding model
);

-- approximate nearest-neighbor search
CREATE INDEX ON documents
    USING hnsw (embedding vector_cosine_ops);

-- find the 10 closest chunks to a query
SELECT id, content
FROM documents
ORDER BY embedding <=> $1::vector   -- <=> is cosine distance
LIMIT 10;
```

Pair that with an embedding model. If you're already running Ollama (and if you're doing local RAG, you probably are), the embedding step is one API call:

```bash
curl http://localhost:11434/api/embed \
  -d '{"model": "nomic-embed-text", "input": "how do I back up my Postgres instance?"}'
```

You store the returned vector, and you're doing RAG. This is the floor — and it's been the floor for a couple years now. The question was never "can Postgres do vector search," it was "does it scale far enough to matter."

---

## What Just Changed: pg_vectorsearch

The thing that hit the Hacker News front page recently is [Timescale's `pg_vectorsearch`](https://github.com/timescale/pg_vectorsearch) — a Postgres extension that sits on top of pgvector and adds a new index type that's genuinely faster than both `IVFFlat` and `HNSW` on real workloads.

The headline claim is specific and worth quoting carefully: it's **an index that's faster than pgvector's IVFFlat and HNSW.** The index is built on **StreamingDiskANN** (a graph-based ANN algorithm originally from Microsoft), and the advantage isn't just raw recall — it's that the index is **memory-mapped and loads as you stream it**, so you don't need the whole index resident in RAM before you can query.

That last part is the one that matters for homelabbers. HNSW is RAM-hungry; a big index wants to be fully in memory or query latency tanks. StreamingDiskANN pages the graph in from disk, which means a large index on a small machine (my Mac mini, your 4 GB LXC) behaves *way* better than HNSW does at the same footprint.

Installing it:

```sql
-- pg_vectorsearch requires pgvector first
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;   -- bundled companion
CREATE EXTENSION IF NOT EXISTS pg_vectorsearch;

-- build the new index type
CREATE INDEX ON documents
    USING streaming_diskann (embedding vector_cosine_ops);
```

Note the extension name `vectorscale` in there — Timescale ships pg_vectorsearch as part of a small stack, and it pulls in what it needs. It also works on plain Postgres; you're not signing up for TimescaleDB the time-series database to use it. That's a real distinction, because a lot of people hear "Timescale" and assume it's a fork.

The practical upshot: the index that used to be the "use a real vector DB" argument — the one that beats pgvector at scale — now lives *inside Postgres*. The ceiling moved up.

---

## My Actual Config

Here's the shape of what I run, so you have something concrete to copy rather than a generic snippet. This assumes Postgres 16+, pgvector, and the Timescale extension all installed (on Debian/Ubuntu: `postgresql-16-pgvector` from PGDG, then `pg_vectorsearch` from Timescale's apt repo).

```sql
-- schema
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_vectorsearch;

CREATE TABLE chunks (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source      text NOT NULL,               -- which file/URL the chunk came from
    content     text NOT NULL,
    embedding   vector(768) NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- the index — streaming_diskann, cosine distance
CREATE INDEX chunks_embedding_idx
    ON chunks USING streaming_diskann (embedding vector_cosine_ops);

-- hybrid filter: search only docs from one source
SELECT c.id, c.content, c.source
FROM chunks c
WHERE c.source = 'postgres-backups'
ORDER BY c.embedding <=> $1::vector
LIMIT 10;
```

Two things I've learned the hard way that the tutorials gloss over:

1. **`vector_cosine_ops` is not cosine similarity.** The `<=>` operator returns *cosine distance* (`1 - similarity`), so smaller is better. If you sort descending you're getting the *least* similar rows. I've made this mistake and so has half of Reddit.
2. **Keep your chunking consistent with your embedding model.** `nomic-embed-text` is built for ~512-token chunks; shoving a 2,000-token page into one vector wastes the model. Chunk first, embed the chunks, store one row per chunk. RAG quality lives or dies on the chunking, not the index.

---

## When Postgres Is Enough (the decision tree)

I don't want you to over-provision. Adding Qdrant or Weaviate to your homelab because a blog post said "Postgres can do vector search *but*" is exactly the kind of reflex that got us running seven containers when one would do. So here's my actual rule:

**Postgres (pgvector + pg_vectorsearch) is enough when:**

- You're under **~5–10 million vectors.** Below that, the new index keeps you comfortably in the "fast enough" zone, and honestly HNSW did too.
- You need **metadata filtering** alongside vector search (e.g., "only my markdown notes, created this year"). Postgres filters and vectors *in one query*, which is genuinely nicer than fanning out to a separate service.
- You want **one less container** and **one less thing to back up.** Your [database backup playbook](/blog/2026-06-20-database-management-playbook-homelab/) already covers Postgres. A dedicated vector DB is a *second* backup strategy, a *second* auth layer, a *second* thing that can silently fall over.
- Your scale is **personal or small-team RAG** — your notes, your docs, your homelab wiki, a handful of users.

**Move to a dedicated vector DB (Qdrant / Weaviate / Pinecone) when:**

- You're heading **past ~50 million vectors** and latency is a real product requirement, not a "this feels slow" complaint.
- You need **managed, multi-tenant, geographically distributed** search with SLAs. (Pinecone's whole pitch is "don't think about it," and for a startup that's worth real money.)
- You need **advanced ANN features** — filtered-search-at-scale performance, built-in re-ranking, quantization tuning — that you'd otherwise hand-roll in SQL.
- You're building something you'd **put on a resume** as production infrastructure, not something you run for yourself.

The honest middle: most self-hosters will never cross that line. If you do, the good news is that migrating *out* of pgvector later is straightforward — you re-embed nothing, you just re-export vectors. Starting in Postgres isn't a trap; it's the reversible default.

---

## The Honest Limits

I promised I wouldn't write a cheerleading post, so here's what still stings:

- **Recall vs. speed is a real dial.** ANN indexes trade recall for speed, and `streaming_diskann` is no exception. For most RAG that trade is invisible; if you need *exact* nearest neighbors, you're doing a brute-force scan and Postgres will be slower than a purpose-built engine tuned for it.
- **Embedding dimensions and models are on you.** Postgres stores and searches vectors; it doesn't help you pick a good embedding model or chunk well. That's the actual hard part of RAG, and no index saves you from bad embeddings.
- **`pg_vectorsearch` is young.** The Timescale extension is new, it's fast-moving, and the `streaming_diskann` index is under active development. Pin your versions and don't treat it as frozen the way you'd treat core Postgres.
- **It's still an extension ecosystem.** You're now depending on pgvector *and* a Timescale extension *and* whatever Postgres version they support. That's fine, but it's one more moving part than "apt install postgresql."

None of that changes the core point. For the overwhelming majority of people running RAG on their own hardware, the answer to "do I need a separate vector database?" is no — and it just got more confidently no.

---

## The Verdict

The self-hosted RAG stack is finally a *real question* with a boring answer: **the database you already run does vector search well enough, and it keeps getting better.** You don't need a sixth container for Pinecone. You need pgvector, the new `pg_vectorsearch` index, a decent embedding model, and discipline about chunking.

That's the bridge between the two things this site keeps hammering on — [Postgres for everything](/blog/2026-08-20-postgres-for-everything-homelab/) and [local LLMs you actually run](/blog/2026-06-12-local-llms-mac-mini-practical-guide/). They were always meant to meet, and now the road between them is paved.

Spin up Qdrant when you've earned it — when you're at eight figures of vectors and latency is on a dashboard somewhere. Until then, stop installing a separate vector database and point RAG at the Postgres that's already in your stack.
