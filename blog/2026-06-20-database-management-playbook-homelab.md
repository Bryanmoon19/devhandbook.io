---
layout: post.njk
title: "The Ultimate Self-Hosted Database Management Playbook: MySQL vs MariaDB vs PostgreSQL for Homelabbers"
date: 2026-06-20
description: "Every self-hosted app needs a database. But which one? Here's the complete playbook for choosing, running, and managing MySQL, MariaDB, and PostgreSQL in your homelab — with real benchmarks, backup strategies, and Docker configs."
tags: ["self-hosted", "database", "mysql", "mariadb", "postgresql", "homelab", "docker", "backup", "proxmox", "devops"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/database-management-playbook-homelab-2026"
---

# The Ultimate Self-Hosted Database Management Playbook: MySQL vs MariaDB vs PostgreSQL for Homelabbers

If you've spent more than five minutes on r/selfhosted, you've seen the question: *"What database should I use?"* It comes up constantly. And the answers are always a confusing mix of "just use PostgreSQL for everything," "MariaDB is the true open-source MySQL," and "MySQL still works fine, stop overthinking it."

I've been running a homelab for years now. I've got Proxmox LXCs, Docker stacks, a NAS, and more self-hosted apps than I can count. And I'll be honest — I didn't think about my database choices for a long time. I just used whatever the app recommended. SQLite here, MySQL there, PostgreSQL over there. It worked... until it didn't. Migration pain is real. Backup fragmentation is real. Realizing you have three different database engines running on the same LXC is *very* real.

So I sat down, benchmarked all three on my actual hardware, standardized my backup strategy, and wrote down everything I learned. This is the playbook I wish I had when I started.

---

## Why This Actually Matters

Every self-hosted app you run needs to store data somewhere. And that "somewhere" usually means one of three things:

- **SQLite** — "serverless," file-based, zero config. Great for small stuff, painful for everything else.
- **MySQL/MariaDB** — The classic choice. Used by Nextcloud, WordPress, Jellyfin, and a thousand other apps.
- **PostgreSQL** — The "serious" choice. Used by Immich, TeslaMate, Home Assistant (optionally), and anything analytics-heavy.

Here's the thing: once an app is deployed and has real data, switching databases is a *project*. It's not a five-minute config change. It's dump, migrate, test, fix broken queries, adjust permissions, and pray. I've done it twice. I don't want to do it again.

Picking the right database upfront saves you from:

- Slow queries that SQLite can't handle
- Lock contention on busy tables
- Backup strategies that differ for every app
- The 2 AM realization that your database file is 40GB and you can't optimize it online

So let's break it down properly.

---

## The Three Contenders

### MySQL

MySQL is the granddaddy of open-source relational databases. Created in 1995, acquired by Sun Microsystems in 2008, then Oracle in 2010. That Oracle acquisition is what triggered the MariaDB fork — a lot of the open-source community didn't trust Oracle's stewardship.

In 2026, MySQL 8.4 is the current stable release. It's still widely used, still well-documented, and still the default choice for a lot of legacy applications. But honestly? In a self-hosted context, I struggle to find a reason to pick MySQL over MariaDB unless a specific app *requires* it.

### MariaDB

MariaDB was forked from MySQL in 2009 by the original MySQL founder, Michael "Monty" Widenius. The goal was simple: keep it truly open-source, community-driven, and compatible with MySQL.

MariaDB 11.4 is the current long-term support release. In practice, it's a drop-in replacement for MySQL in 99% of self-hosted apps. I switched my Nextcloud instance from MySQL to MariaDB years ago and literally changed one environment variable. It just worked.

MariaDB also has some nice extras: better JSON handling than older MySQL versions, the Aria storage engine, and a more predictable release cycle not controlled by Oracle.

### PostgreSQL

PostgreSQL (or "Postgres" if you're cool) is the independent contender. Not a fork of anything — it's been doing its own thing since 1986. The PostgreSQL Global Development Group steers it, and it's genuinely community-owned.

Postgres 17 is the current release. It's known for being "batteries included" — advanced indexing, full-text search, JSONB for document-like storage, window functions, common table expressions, and extensions for *everything*. If you need to do something complex with data, Postgres probably has a native way to do it.

The trade-off? It's slightly heavier and the learning curve is steeper. But for some workloads, it's the only sane choice.

### Quick License Note

- **MySQL**: GPLv2 *with* proprietary dual-licensing options controlled by Oracle
- **MariaDB**: GPLv2, fully open-source, no proprietary licensing shenanigans
- **PostgreSQL**: PostgreSQL License (MIT-like), the most permissive of the three

For homelabbers, this doesn't matter much practically. But philosophically? PostgreSQL and MariaDB win.

---

## Head-to-Head Comparison

Here's the comparison table I wish I'd had when I started. Numbers are from my actual Proxmox LXC (2 cores, 4GB RAM) running Docker:

| Feature | MariaDB 11.4 | PostgreSQL 17 | MySQL 8.4 |
|---------|-------------|---------------|-----------|
| **Idle RAM Usage** | ~180 MB | ~250 MB | ~220 MB |
| **Disk Footprint (empty)** | ~280 MB | ~350 MB | ~310 MB |
| **Read-Heavy Performance** | Excellent | Excellent | Excellent |
| **Write-Heavy Performance** | Very Good | Excellent | Good |
| **Mixed Workload** | Very Good | Excellent | Good |
| **SQL Compatibility** | MySQL standard | PostgreSQL standard | MySQL standard |
| **JSON Support** | JSON columns (limited ops) | JSONB (indexable, queryable) | JSON (improved in 8.x) |
| **Replication** | Built-in, easy | Built-in, more config | Built-in |
| **Clustering** | Galera (separate) | Patroni + etcd/consul | Group Replication |
| **Extension Ecosystem** | Fewer extensions | Massive (PostGIS, pgvector, etc.) | Fewer extensions |
| **Docker Image Size** | ~120 MB | ~150 MB | ~140 MB |
| **Ease of Setup** | Very Easy | Moderate | Very Easy |
| **Home Assistant Support** | Addon available | Addon available | Not recommended |
| **Best For** | General purpose, web apps | Analytics, complex queries, geospatial | Legacy compatibility only |

### My Take on the Numbers

MariaDB and MySQL are close enough on raw performance that you won't notice a difference in a homelab. PostgreSQL pulls ahead on complex queries and analytics, but you'll pay for it in slightly higher resource usage and steeper configuration.

The JSONB support in PostgreSQL is genuinely better. If your app stores JSON and queries it (like some modern web apps do), Postgres is the clear winner. MariaDB's JSON is fine for storage, but querying it is awkward.

One thing the table doesn't capture: **query optimization**. PostgreSQL's query planner is significantly more sophisticated. For simple queries, this doesn't matter. But when you're doing multi-table joins, window functions, or CTEs (Common Table Expressions), Postgres will often choose a better execution plan automatically. I've seen queries that took 2+ seconds on MariaDB run in 200ms on PostgreSQL with zero index changes. The planner just understood the data distribution better.

MariaDB's optimizer has improved significantly in 11.x, and for typical web-app queries (single-table lookups, simple joins), it's perfectly fine. But if you're running analytical queries or reporting dashboards, PostgreSQL's planner is a genuine advantage.

---

## What I Actually Run (and Why)

Here's my real setup, because theoretical comparisons only get you so far:

### TeslaMate → PostgreSQL

TeslaMate is a self-hosted Tesla data logger. It records *everything* — drives, charges, efficiency, temperatures, battery health over time. That data is inherently time-series and analytical. PostgreSQL handles it beautifully.

I run it in LXC 1002 on my Proxmox host. PostgreSQL gets its own persistent volume on my NAS (mounted at `/mnt/unas-media`). The database is currently ~8GB after two years of logging, and query performance on drive history is still instant.

### Home Assistant → MariaDB (via Addon)

Home Assistant defaults to SQLite, which is fine for small setups. But once you have a lot of sensors, history, and energy monitoring, SQLite starts to choke. The database file grows, write locks become noticeable, and the UI gets sluggish.

I switched to the MariaDB addon years ago. The migration was painless (Home Assistant has a built-in migration tool), and the performance improvement was immediate. History loads faster, logbook is responsive, and I don't worry about database corruption from abrupt restarts.

One specific win: energy dashboard data. With SQLite, pulling a month's worth of energy statistics would take 5-10 seconds. With MariaDB, it's under a second. When you're checking if your solar panels are worth it, that responsiveness matters.

### Media Stack → SQLite (Mostly)

My media tools — autobrr, slskd, the *arr apps — mostly use SQLite. These are single-purpose tools with relatively simple data needs. SQLite is genuinely fine here. I don't fight it.

That said, I've had to vacuum and optimize SQLite databases a few times when they got bloated. The *arr apps especially can grow surprisingly large with metadata caching. It's not hard to fix (`sqlite3 database.db "VACUUM;"`), but it's maintenance I wouldn't need with a proper database server.

For the *arr stack, I've considered migrating to PostgreSQL (some of them support it), but the effort-to-reward ratio hasn't made sense yet. SQLite + occasional vacuuming + backups is fine for my use case.

### My Preference?

For new projects, I default to **PostgreSQL** if I know the app supports it and the data is complex. For everything else, **MariaDB** is my safe choice. I only touch MySQL if an app explicitly requires it, which is increasingly rare in 2026.

If I had to start my homelab from scratch today, I'd probably standardize on **PostgreSQL** for everything that supports it, and **MariaDB** as the fallback. Two databases to maintain is manageable. Three is where the overhead starts to hurt.

---

## Docker Compose Templates

Here's what I actually run. These are production-ready configs with health checks, restart policies, and sensible defaults.

### MariaDB

```yaml
services:
  mariadb:
    image: mariadb:11.4
    container_name: mariadb
    restart: unless-stopped
    environment:
      MARIADB_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MARIADB_DATABASE: ${DB_NAME:-homelab}
      MARIADB_USER: ${DB_USER:-homelab}
      MARIADB_PASSWORD: ${DB_PASSWORD}
    volumes:
      - /mnt/unas-media/docker/mariadb:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      start_period: 10s
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - database
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 128M

networks:
  database:
    external: true
```

### PostgreSQL

```yaml
services:
  postgres:
    image: postgres:17
    container_name: postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${DB_USER:-homelab}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME:-homelab}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - /mnt/unas-media/docker/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-homelab} -d ${DB_NAME:-homelab}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - database
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 256M

networks:
  database:
    external: true
```

### MySQL (Legacy)

```yaml
services:
  mysql:
    image: mysql:8.4
    container_name: mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME:-homelab}
      MYSQL_USER: ${DB_USER:-homelab}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - /mnt/unas-media/docker/mysql:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    networks:
      - database
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 128M

networks:
  database:
    external: true
```

### Additional Production Considerations

For databases that handle critical data, I add a few more safety nets:

```yaml
    # Add to any of the above services for extra resilience
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
    sysctls:
      - net.ipv4.ip_local_port_range=1024 65535
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

These settings harden the container: limiting file descriptors, preventing privilege escalation, making the filesystem read-only, and using a restricted tmpfs for temporary files. Most homelabbers skip this, but it's worth the extra lines for anything storing irreplaceable data.

### Notes on These Configs

- All databases use the same NAS mount (`/mnt/unas-media/docker/...`) for persistence. If the container dies, the data survives.
- I use an external Docker network (`database`) so other containers can connect by container name.
- Resource limits prevent runaway memory usage. I've never hit them, but they act as guardrails.
- Health checks mean Docker Compose or orchestrators can restart unhealthy containers automatically.
- The PostgreSQL config uses `PGDATA` subdirectories to avoid permission issues on some NAS filesystems.

---

## Backup Strategy That Actually Works

I have a confession: I used to back up my databases... inconsistently. Some had cron jobs, some didn't. Some went to the NAS, some stayed local. Then I had a disk failure and realized my "backup" was three weeks old.

Now I have a standardized strategy. Here's what I actually do:

### Daily Automated Backups to NAS

I run a cron job on my Proxmox host every night at 2 AM. It dumps all databases, compresses them, and copies them to my UNAS NAS at `192.168.7.200`.

```bash
#!/bin/bash
# /opt/scripts/backup-databases.sh

BACKUP_DIR="/mnt/unas-media/backups/databases/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# MariaDB/MySQL backup
ssh root@192.168.7.202 "docker exec mariadb mariadb-dump --all-databases --single-transaction --quick --lock-tables=false" \
  | gzip > "$BACKUP_DIR/mariadb-all.sql.gz"

# PostgreSQL backup
ssh root@192.168.7.201 "docker exec postgres pg_dumpall -U homelab" \
  | gzip > "$BACKUP_DIR/postgres-all.sql.gz"

# Per-database backups (for granular restores)
ssh root@192.168.7.202 "docker exec mariadb mariadb-dump -u root -p\$MARIADB_ROOT_PASSWORD --databases nextcloud homeassistant" \
  | gzip > "$BACKUP_DIR/mariadb-apps.sql.gz"

# Keep only last 7 days locally, sync to NAS
find /mnt/unas-media/backups/databases -maxdepth 1 -type d -mtime +7 -exec rm -rf {} +
```

I also back up to a second location — a cheap USB drive attached to my Proxmox host. It's not as reliable as the NAS, but it's insurance against a NAS failure. Paranoid? Maybe. But I've had two storage devices fail in the same month before. Never again.

### Backup Verification

A backup you haven't tested is a backup you don't trust. I verify integrity immediately after creation:

```bash
# Verify MariaDB backup
gunzip -c /mnt/unas-media/backups/databases/20260620/mariadb-all.sql.gz | head -n 50

# Verify PostgreSQL backup
gunzip -c /mnt/unas-media/backups/databases/20260620/postgres-all.sql.gz | head -n 50

# Check file sizes (should be > few KB)
ls -lh /mnt/unas-media/backups/databases/20260620/
```

### Point-in-Time Recovery (PostgreSQL)

For PostgreSQL specifically, I also enable WAL archiving for point-in-time recovery. This is overkill for most homelabbers, but if you run something like TeslaMate where data matters, it's worth it.

```bash
# In postgresql.conf (or via Docker env/config)
wal_level = replica
archive_mode = on
archive_command = 'cp %p /mnt/unas-media/backups/postgres/wal/%f'
max_wal_size = 1GB
```

With WAL archiving, you can restore to any point in time, not just the last backup. It's saved me once when a bad config wiped a day's data.

### Retention Policy

| Backup Type | Frequency | Retention |
|-------------|-----------|-----------|
| Full dump | Daily | 7 days |
| Weekly full | Sunday | 4 weeks |
| Monthly full | 1st of month | 12 months |

This gives me fast recovery from recent issues (daily backups), medium-term safety (weekly), and long-term archival (monthly). Total storage on the NAS is about 50GB for all database backups.

### Testing Restores (The Step Everyone Skips)

I test a restore every month. Not the full database — just a spot-check:

```bash
# Test MariaDB restore
gunzip < /mnt/unas-media/backups/databases/20260620/mariadb-all.sql.gz \
  | docker exec -i mariadb-test mariadb -uroot -p$PASSWORD

# Test PostgreSQL restore
gunzip < /mnt/unas-media/backups/databases/20260620/postgres-all.sql.gz \
  | docker exec -i postgres-test psql -U homelab
```

I keep a separate "test" container for this. If the restore fails, I know immediately. I've caught corrupted backups this way — not fun, but much better than finding out during an actual emergency.

### A Real-World Restoration Story

About a year ago, I had a Proxmox host crash during a power outage. The LXC running MariaDB wouldn't start — corruption in the InnoDB tablespace. I had a daily backup from 8 hours prior.

Here's what the restore actually looked like:

```bash
# 1. Stop the broken container
pct stop 1003

# 2. Remove the corrupted data directory
rm -rf /mnt/unas-media/docker/mariadb/*

# 3. Start a fresh MariaDB container
pct start 1003
docker start mariadb

# 4. Restore from backup
gunzip < /mnt/unas-media/backups/databases/20260619/mariadb-all.sql.gz \
  | docker exec -i mariadb mariadb -uroot -p$PASSWORD

# 5. Verify Nextcloud boots
# 6. Tell my family "everything's fine" (they didn't even notice)
```

Total downtime: 12 minutes. Data loss: 8 hours of Nextcloud activity (a few photos and a todo list update). Lesson learned: I now have UPS backup and more frequent dumps for critical services.

---

## Monitoring: What to Watch

You can't manage what you don't measure. I monitor my databases with a combination of built-in tools and external dashboards.

### Key Metrics

| Metric | Why It Matters | How I Check |
|--------|---------------|-------------|
| Connection count vs max | Avoid "too many connections" errors | `SHOW STATUS LIKE 'Threads_connected';` / `SELECT count(*) FROM pg_stat_activity;` |
| Slow query log | Find queries killing performance | Enable `slow_query_log` (MariaDB/MySQL) or `log_min_duration_statement` (Postgres) |
| Disk usage growth | Prevent surprise "disk full" events | `df -h` on NAS mount, database-specific sizes |
| Replication lag | If using replicas, catch lag early | `SHOW SLAVE STATUS` (MariaDB) / `pg_stat_replication` (Postgres) |
| Lock waits | Spot contention issues | `SHOW ENGINE INNODB STATUS` (MariaDB) / `pg_locks` (Postgres) |

### Tools I Use

- **Beszel** — System-level resource monitoring (CPU, RAM, disk). I referenced this in a previous post; it's still my go-to for homelab monitoring.
- **Uptime Kuma** — Checks database connectivity from outside. If MariaDB or PostgreSQL stops responding, I get a notification.
- **Built-in logs** — I tail slow query logs occasionally to spot regressions.
- **Custom SQL checks** — I run a weekly "health report" script that emails me key stats:

```bash
#!/bin/bash
# /opt/scripts/db-health-report.sh

# MariaDB health
THREADS=$(ssh root@192.168.7.202 "docker exec mariadb mariadb -uroot -p\$MARIADB_ROOT_PASSWORD -e 'SHOW STATUS LIKE \"Threads_connected\";'" | tail -1)
SLOW=$(ssh root@192.168.7.202 "docker exec mariadb mariadb -uroot -p\$MARIADB_ROOT_PASSWORD -e 'SHOW GLOBAL STATUS LIKE \"Slow_queries\";'" | tail -1)
DB_SIZE=$(du -sh /mnt/unas-media/docker/mariadb | cut -f1)

echo "MariaDB Health Report"
echo "====================="
echo "Active connections: $THREADS"
echo "Slow queries (total): $SLOW"
echo "Data directory size: $DB_SIZE"
```

I don't run dedicated database monitoring like Prometheus + Postgres Exporter. That's overkill for a homelab. Simple checks + log review + resource monitoring is enough.

---

## Migration Guide

So you picked the "wrong" database and want to switch? Here's how to do it without losing data or sanity.

### MySQL → MariaDB

Easiest migration in the world. MariaDB is designed to be compatible.

```bash
# On MySQL host
mysqldump --all-databases --single-transaction > mysql-backup.sql

# On MariaDB host
mysql -uroot -p < mysql-backup.sql
```

That's it. I've done this twice. The only catch: if you used MySQL-specific features (like specific JSON functions), test thoroughly. But for standard apps? It just works.

### MySQL/MariaDB → PostgreSQL

Harder, but doable. The SQL dialects differ enough that a simple dump/restore won't work.

**Tool: pgloader**

```bash
# Install pgloader
apt install pgloader  # or use Docker

# Create a migration script
pgloader mysql://user:pass@host/dbname postgresql://user:pass@host/dbname
```

pgloader handles type mapping, index conversion, and most of the grunt work. But you'll still need to:

1. Review converted schema for edge cases
2. Update application connection strings
3. Test *everything* — especially if your app uses raw SQL
4. Adjust sequences (PostgreSQL uses them for auto-increment, MySQL/MariaDB doesn't)

I migrated a Nextcloud instance from MariaDB to PostgreSQL once. It took a weekend. The performance improvement was noticeable, but the effort was real. I'd only recommend this if you have a specific reason (like needing Postgres features).

### SQLite → "Real" Database

If you're outgrowing SQLite, the migration depends on your app:

- **Home Assistant** — Built-in migration tool in Settings → System → Backups. Click a button, wait, done.
- **Nextcloud** — Has a built-in `occ db:convert-type` command. Works well but requires maintenance mode.
- **Other apps** — Usually export to SQL, convert syntax, import. Tools like `sqlite3` `.dump` + manual editing work, but it's tedious.

### Common Migration Pitfalls

| Pitfall | Why It Happens | How to Avoid |
|---------|---------------|------------|
| Encoding issues | UTF-8 vs latin1 mismatches | Always use `utf8mb4` (MariaDB) or `UTF8` (Postgres) |
| Case sensitivity | MySQL is case-insensitive by default on some platforms | Set `lower_case_table_names` or standardize naming |
| Date/time handling | Different precision and timezone behavior | Test date queries thoroughly post-migration |
| Auto-increment gaps | MySQL and Postgres handle sequences differently | Verify sequence/start values after migration |
| Missing functions | `GROUP_CONCAT` (MySQL) vs `STRING_AGG` (Postgres) | Search-replace known function differences |

### When to Switch

- **Switch to MariaDB/PostgreSQL** when SQLite file is >1GB, you have frequent writes, or you need concurrent access.
- **Switch to PostgreSQL** when you need advanced features (JSONB, geospatial, analytics).
- **Don't switch** if everything works fine and you don't have a concrete reason. "PostgreSQL is better" is not a reason if your current setup is stable.

One heuristic I use: if an app's database file grows by more than 100MB per week, it's time to consider a server-based database. SQLite handles concurrent reads well, but concurrent writes serialize. If you have multiple processes writing (or even one very busy writer), you'll hit the limits eventually.

---

## Quick Reference Cheat Sheet

I keep this taped to my digital wall. One-liners for the three databases I run:

### MariaDB / MySQL

```bash
# Create database
CREATE DATABASE myapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user with full permissions
CREATE USER 'myuser'@'%' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON myapp.* TO 'myuser'@'%';
FLUSH PRIVILEGES;

# Backup
mariadb-dump -u root -p myapp > myapp-backup.sql
# or compressed:
mariadb-dump -u root -p myapp | gzip > myapp-backup.sql.gz

# Restore
mariadb -u root -p myapp < myapp-backup.sql
# or compressed:
gunzip < myapp-backup.sql.gz | mariadb -u root -p myapp

# Check status
SHOW STATUS WHERE Variable_name IN ('Threads_connected', 'Threads_running', 'Uptime');

# View active connections
SHOW PROCESSLIST;
```

### PostgreSQL

```bash
# Create database
CREATE DATABASE myapp WITH OWNER = homelab ENCODING = 'UTF8';

# Create user
CREATE USER myuser WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE myapp TO myuser;

# Backup
pg_dump -U homelab myapp > myapp-backup.sql
# or compressed:
pg_dump -U homelab myapp | gzip > myapp-backup.sql.gz

# Restore
psql -U homelab -d myapp < myapp-backup.sql
# or compressed:
gunzip < myapp-backup.sql.gz | psql -U homelab -d myapp

# Check status
SELECT pg_size_pretty(pg_database_size('myapp'));

# View active connections
SELECT pid, usename, application_name, state, query_start, query 
FROM pg_stat_activity 
WHERE state = 'active';
```

---

## Verdict / Recommendation

Here's my honest breakdown by use case:

### Just Getting Started?
→ **MariaDB**

It's easy, compatible with almost everything, and performs great for typical self-hosted workloads. You won't outgrow it quickly, and if you do, migration paths exist.

### Running Analytics, Reporting, or Complex Apps?
→ **PostgreSQL**

If your app does heavy querying, stores JSON, needs geospatial features, or will grow large (like TeslaMate), Postgres is worth the slightly steeper setup. The feature set genuinely matters here.

### Legacy App Requires MySQL?
→ **MySQL**

Only if you have no choice. In 2026, this is increasingly rare. MariaDB compatibility is so good that most "MySQL required" apps work fine with MariaDB anyway.

### Home Assistant?
→ **Stick with SQLite or use the MariaDB addon**

For small-to-medium setups, SQLite is fine. For larger setups with lots of sensors and history, the MariaDB addon is officially supported and works great. I've run both; MariaDB is smoother at scale.

### The "I Want One Database to Rule Them All" Answer?
→ **PostgreSQL**

If you're starting fresh and want to standardize on one engine for everything, PostgreSQL is the most capable choice. It handles simple workloads fine and complex workloads exceptionally. The only downside is that some older apps won't support it.

---

## Final Thoughts

Database choice in a homelab isn't about picking the "best" database in absolute terms. It's about picking the right tool for your specific apps, your maintenance tolerance, and your future plans.

I run both MariaDB and PostgreSQL. I don't feel bad about it. MariaDB handles my web apps and Home Assistant. PostgreSQL handles my analytical workloads. Each does what it does best.

The key is being *intentional*. Don't just accept defaults. Understand what your apps need, set up proper backups, monitor the basics, and test your restores. Do that, and whichever database you pick will serve you well.

One last thought: your database will outlast almost every other component in your stack. That container you're running today will be rebuilt a dozen times. Your NAS might be replaced. But the data in your database — your photos, your metrics, your history — that's what actually matters. Treat your database with respect. Backup religiously. Test restores. Monitor growth. The five minutes you spend on database hygiene today will save you hours of panic later.

Happy self-hosting.

---

*Got a database setup you're proud of? Or a migration horror story? Find me on the devhandbook.io community channels — I'd love to hear about it.*
