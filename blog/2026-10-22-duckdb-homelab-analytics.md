---
layout: post.njk
title: "DuckDB for Homelab Analytics: The Zero-Server Engine That Complements Postgres, Not Replaces It"
date: 2026-10-22
description: "DuckDB 2.0.0 just shipped as the project's first LTS release, and it hit the Hacker News front page at 386 points. If you run 'Postgres for everything' on a homelab, DuckDB is the missing half: a zero-server, in-process analytical engine that crunches Parquet, CSV, and JSON without standing up a single container. Here's what changed in 2.0, how to point it at your homelab data, and — honestly — when Postgres still wins."
tags: ["duckdb", "analytics", "olap", "postgres", "parquet", "homelab", "self-hosted", "data", "sql", "lts", "columnar", "lxc", "proxmox", "mac-mini"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-22-duckdb-homelab-analytics/"
affiliate: false
cta: true
---

Here's the tension I've been living with for months, and I don't think I'm alone.

I run [Postgres for everything](/blog/2026-08-20-postgres-for-everything-homelab/) — Redis, cron, queues, search, all collapsed into one instance on a Mac mini. And that's genuinely great for the *system of record* side of a homelab: the stuff that has to be always on, always correct, always answering a query within a few milliseconds because some app is waiting on it.

But there's a second kind of data work that Postgres is just *bad* at, and I've been quietly avoiding it because the usual answer is "spin up ClickHouse or Apache Spark" — which is insane for a box with two cores and 4GB of RAM. That work is **analytics**: crunching a pile of logs, joining a directory of Parquet files, answering "what's my actual power draw over the last 90 days" from a CSV that a sensor dumped somewhere.

This week the answer to that second problem got a lot more real. **DuckDB 2.0.0 shipped as the project's first LTS release**, it hit the Hacker News front page at 386 points, and it's the natural companion to the "Postgres for Everything" post that this site keeps coming back to. Where Postgres is your always-on system of record, DuckDB is your **zero-server analytical engine** — no daemon, no container, no network port. It's a library you `import`, point at files, and query with SQL.

This post is the homelab angle on DuckDB 2.0. What the LTS release actually changes, how to point it at the data your homelab already generates, and the honest line where Postgres is still the right tool.

---

## What DuckDB Is (and Why It's Different From Every Database You Already Run)

Most databases — Postgres, MySQL, SQLite included — are what the data people call **row-oriented, transactional engines**. They're optimized to write a row, read a row, update a row, keep it consistent, and answer "give me the current state of this one record" as fast as possible. That's the right tradeoff when the query is `SELECT * FROM users WHERE id = 42` and an app is waiting on it.

DuckDB is the opposite shape. It's **column-oriented and analytical**, built for the query that says "give me the average, grouped by day, across 40 million rows." It stores data by column instead of by row, which means scanning a single column across a huge dataset doesn't touch the columns you don't care about. It vectorizes execution. It's absurdly fast at the kind of aggregations that make Postgres sweat.

But the thing that matters most for a homelab is this: **DuckDB is not a server.** There's no daemon to run, no container to deploy, no port to expose, no auth to configure. It's an in-process library — a single file you embed in Python, R, Node, Java, or call from its own CLI. You `pip install duckdb` or `brew install duckdb`, point it at a file, and run SQL against it. When the query is done, it's gone. Nothing is listening on a socket, nothing needs to be backed up, nothing can silently fall over at 3 AM.

The "zero-server" part is not a limitation for analytics. It's the entire pitch. Your homelab already *has* data sitting in files — logs, metrics exports, Parquet dumps, CSVs from sensors, JSON from APIs. DuckDB lets you query that data **in place, without ingesting it into a database first.** You don't build a pipeline. You run a query.

---

## What Changed in 2.0.0 LTS

The thing that pushed this onto the HN front page is that DuckDB 2.0.0 is the first release the project has designated **Long-Term Support**. Before this, DuckDB moved fast — new versions every couple months, breaking changes allowed, and "pin your version" was the standing advice. For a tool you might point at years of accumulated homelab data, that was a mild anxiety: is the query I wrote six months ago still going to run?

LTS changes that. The headline promises are worth stating plainly:

- **A stable, supported release line.** 2.0.x gets bug fixes and maintenance for an extended window, so you're not chasing a moving target. For something you might script into a nightly job and forget about for a year, that's the difference between "set and forget" and "why did my cron break."
- **Better Parquet and larger-than-memory workloads.** DuckDB has always been strong on Parquet, but 2.0 tightens the story on working with datasets bigger than RAM by streaming and pushing down filters into file scans. On a small homelab box, "bigger than RAM" is most of your data.
- **A clearer upgrade path.** Going from 1.x to 2.0 is a real, announced break rather than a series of quiet papercuts, and the docs spell out what moved. If you've been holding off on DuckDB because "it's too fast-moving to rely on," 2.0 is the release that answers that objection.

I won't pretend to exhaust the changelog — the point for *this* audience is narrower. LTS means DuckDB just became safe to build small, durable things on top of, which is exactly the kind of tool a homelab needs: powerful enough to be worth learning, stable enough not to punish you for it.

---

## The Companion Framing: Postgres Is the Record, DuckDB Is the Lens

The natural question, if you've read [Postgres for everything](/blog/2026-08-20-postgres-for-everything-homelab/), is "do I need to pick one?" And the answer is no — they solve different halves of the same problem, and they fit together without fighting.

**Postgres is your system of record.** It's always on, it enforces constraints, it's the place your apps write to and read from in real time. It answers "what is the *current* state of this thing" and "what just happened." When an app needs a row back in 2 milliseconds, Postgres is the tool, and trying to make DuckDB fill that role is wrong — DuckDB isn't built for concurrent writes or point lookups, and it'd be a worse database for it.

**DuckDB is your analytical lens.** It's for the questions that happen *after* the fact, in bulk: "over the last year, how has my power draw trended by week," "which of my services burned the most disk in September," "join my DNS logs against my firewall logs and tell me which device is the chattiest." Those are queries over *history*, over *files*, over *data at rest*. They don't need a server, and Postgres shouldn't have to hold all that raw history just so you can occasionally aggregate it.

Concretely, the pattern I've landed on is: **Postgres holds the hot, current state; DuckDB reads the cold, historical data that Postgres doesn't want to store.** You export from Postgres to Parquet (or point DuckDB at `pg` directly — more on that in a second), and the raw logs, metrics dumps, and sensor CSVs live as files that DuckDB queries in place.

Two tools, no conflict. One is the record, one is the lens.

---

## Pointing DuckDB at Your Actual Homelab Data

Here's where it gets fun, because DuckDB's whole trick is that you don't build a pipeline — you just *read the files you already have*.

### The CLI, in one line

```bash
brew install duckdb      # or: pip install duckdb / apt install duckdb
duckdb                   # opens an interactive shell, no server anywhere
```

From there, you can query a CSV sitting anywhere on disk without importing it:

```sql
-- a CSV that some sensor or exporter dumped
SELECT *
FROM read_csv('/mnt/nas/sensors/power_usage_2026.csv')
LIMIT 5;
```

That `read_csv` isn't loading the file into a table. It's reading it lazily, pushing filters down, and returning results. Swap `read_parquet`, `read_json`, or even `read_csv_auto` for auto-detected types and you're off.

### Parquet is the format to settle on

If you take one thing from this post, make it this: **export your analytical data as Parquet, not CSV or JSON.** Parquet is columnar and compressed, which means DuckDB reads only the columns your query touches and skips the rest. A 2GB CSV becomes a few hundred MB of Parquet, and the queries get faster in proportion. It's the format DuckDB was built to love.

Generating it is a one-liner from DuckDB itself:

```sql
-- convert an existing CSV to Parquet, or write a query result out
COPY (SELECT * FROM read_csv_auto('/mnt/nas/sensors/power.csv'))
TO '/mnt/nas/sensors/power.parquet' (FORMAT 'parquet');
```

From then on, query the `.parquet` files directly. No database, no server, just files on your NAS.

### The Postgres bridge: `postgres_scanner`

The thing that ties this back to [Postgres for everything](/blog/2026-08-20-postgres-for-everything-homelab/) is DuckDB's `postgres_scanner`, which lets DuckDB run a query *against your live Postgres instance* and pull the result into DuckDB for analysis. No export step, no cron, no staging tables.

```sql
INSTALL postgres;
LOAD postgres;

ATTACH 'host=192.168.7.201 port=5432 dbname=app user=analytics password=***'
    AS pg (TYPE postgres);

-- run analytics against live Postgres data from DuckDB
SELECT date_trunc('week', created_at) AS week, count(*)
FROM pg.events
GROUP BY 1
ORDER BY 1;
```

This is the bridge that makes the whole "companion" framing concrete. Postgres stays the system of record; DuckDB reaches into it, pulls what it needs, and crunches it with the columnar engine. You get analytical performance on your live data without ever asking Postgres to be an OLAP database — and without standing up a separate analytical service.

---

## A Real Homelab Query, End to End

Let me make this concrete with the kind of question I actually want answered, because abstract "look, SQL!" doesn't help anyone.

Say I want to know my true power draw trend over a quarter. I have a CSV per month from a smart-plug exporter, dumped to the NAS, and a Parquet file of historical readings. In Postgres I'd have to import all of it, index it, and hold it in a database forever. In DuckDB I just:

```sql
-- glue a whole directory of monthly CSVs together and aggregate
SELECT
    date_trunc('day', ts) AS day,
    round(avg(watts), 1)   AS avg_watts,
    round(max(watts), 1)   AS peak_watts
FROM read_csv_auto('/mnt/nas/sensors/power_*.csv', filename = true)
GROUP BY 1
ORDER BY 1;
```

The `power_*.csv` glob reads *every* matching file as one logical table, and `filename = true` gives you a column telling you which file each row came from so you can split by month if you want. No import, no schema, no index. The query runs in a couple hundred milliseconds on a Mac mini and leaves nothing behind.

That's the whole pitch in one example: **the data already exists as files, and DuckDB turns "a directory of files" into "a table you can query."**

---

## When Postgres Still Wins (the Honest Line)

I refuse to write a cheerleading post, so here's where DuckDB is the *wrong* tool and you should keep reaching for Postgres:

- **Point lookups and current state.** If the question is "what's this one record's value right now," DuckDB is the wrong shape. It's not built for single-row fetches, and it's not a place you write to concurrently. Postgres is your system of record for a reason; DuckDB doesn't replace it and shouldn't try.
- **Anything that needs real-time, always-on serving.** DuckDB has no server. If an app needs to query it over a socket 24/7, you'd be bolting on something (like DuckDB's own HTTP extension or a wrapper) that Postgres already gives you for free. For live app queries, Postgres. For batch analysis, DuckDB.
- **Concurrent writes and transactional integrity.** DuckDB is single-writer by design. It's an analytical engine, not a database you run your apps against. If you need multiple writers and ACID guarantees, that's literally what Postgres is for.
- **Small, hot, frequently-updated datasets.** If your "analytics" is a few thousand rows that change constantly and get queried constantly, the overhead of thinking about DuckDB isn't worth it — Postgres handles that trivially, and the analytical edge doesn't matter at that scale.

The framing to hold onto: **DuckDB doesn't compete with Postgres, it complements it.** Postgres holds what's live and must be correct; DuckDB crunches what's historical and just needs to be fast. Trying to make one tool do both is how you end up with either an OLAP query that makes Postgres crawl or a server you didn't need.

---

## The Verdict

DuckDB 2.0.0 LTS landed at a moment when "Postgres for everything" is a settled answer for the system-of-record side of a homelab — and it fills the hole that answer leaves open. Your box already generates a pile of analytical data in files: logs, metrics, sensor CSVs, JSON exports. Until now, querying it meant either ingesting it into Postgres (which doesn't want the raw history) or standing up a whole analytical service (which a 4GB Mac mini doesn't want either).

DuckDB splits that difference perfectly: **a zero-server analytical engine that reads your files in place, and it's now stable enough to build on.** No daemon, no container, no port, no backup story. Install it, point it at a directory of Parquet, and run SQL. Point it at your Postgres with `postgres_scanner` when you want analytics on live data without making Postgres do the heavy lifting.

It's the natural companion to the [Postgres for everything](/blog/2026-08-20-postgres-for-everything-homelab/) post, and it completes a sentence this site has been writing for months: **Postgres is your always-on system of record. DuckDB is the lens you put over it when you want to understand what actually happened.** You don't have to pick one — you run both, and each makes the other's job easier.

If you're running a homelab and you've been avoiding analytics because "that means ClickHouse or Spark," install DuckDB tonight and query a CSV you already have. It'll take you five minutes, and it'll change how you think about the data sitting on your NAS.
