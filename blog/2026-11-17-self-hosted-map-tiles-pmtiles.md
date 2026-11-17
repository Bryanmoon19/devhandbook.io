---
layout: post.njk
title: "Self-Host Map Tiles with PMTiles: Drop Mapbox and the Per-Load Bill"
date: 2026-11-17
description: "PMTiles collapses the entire map stack — tile server, caching layer, CDN config — into a single file you serve from any static bucket. Here's how to replace Mapbox (and its $5-per-1,000-loads bill) with a self-hosted, self-owned map layer using PMTiles, MapLibre GL JS, and Cloudflare R2."
tags: ["pmtiles", "protomaps", "maplibre", "mapbox", "self-hosted", "maps", "geospatial", "cloudflare", "r2", "vector-tiles", "openstreetmap", "serverless", "homelab"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-17-self-hosted-map-tiles-pmtiles/"
affiliate: false
cta: true
---

# Self-Host Map Tiles with PMTiles: Drop Mapbox and the Per-Load Bill

For years, if your app needed an interactive map, the math was quietly rigged against you. You built the thing, shipped it, got some traction — and then the bill arrived. Mapbox charges **$5 per 1,000 map loads** past the free tier. Google's terms are a maze of SKUs and quota surprises. The moment your project goes viral is the exact moment the map stops being a feature and starts being a liability.

Here's the thing the last few years quietly fixed: **you no longer need to rent a map.** A format called PMTiles turns an entire interactive world map into *one file* that you serve from any static bucket. No tile server. No PostGIS. No caching layer. No per-load billing. You upload a file, point MapLibre at it, and you own the map layer outright.

This is the self-hoster's version of the same un-bundling we've been doing to everything else — replace the SaaS line item with a file you control. Here's the honest, hands-on guide.

---

## The Old Way: Why Maps Got So Expensive

To understand why PMTiles is a big deal, you have to see what it replaces.

A classic "slippy map" (the kind Google Maps and Mapbox serve) is built from *millions of tiny image or vector tiles*, each covering a small square of the world at a given zoom level. Your browser asks for exactly the tiles it needs as you pan and zoom. That's elegant for the user, but it means:

1. **You need a tile server** — a dedicated backend that knows how to fetch, cache, and hand out thousands of tiles per second. That's PostGIS, a caching layer, load balancers, and an ops burden most indie devs never wanted.
2. **Or you pay someone else to run it** — which is where Mapbox, Google, MapTiler, and the rest come in. They run the tile infrastructure and meter you per load. Convenient, until it isn't.

The per-load meter is the trap. A tile server's *marginal cost* per request is fractions of a cent, but the *metered price* is $5 per thousand. That spread is the whole SaaS business model — and it's why a map can out-cost the rest of your infrastructure combined once traffic spikes.

PMTiles attacks this at the root: **what if the "tile server" was just a file and a static file server you already run?**

---

## What PMTiles Actually Is

[PMTiles](https://github.com/protomaps/PMTiles) (from the [Protomaps](https://protomaps.com) project, 3,200+ GitHub stars) is an **archive format for map tiles stored in a single file**. The key insight is in how it's laid out on disk.

Instead of millions of individual tiles in millions of individual files, PMTiles packs all of them into one file with a **pyramid structure and a directory index** at the front. When the map needs tile (z, x, y), the client does a tiny HTTP **Range request** — it asks the server for *just those bytes* of the file. Your static host (S3, Cloudflare R2, nginx, a plain web server) hands back a few kilobytes. No custom logic, no tile server, no database.

The format spec is small (currently **version 3**), open, and there are client libraries for JavaScript, Python, Go, and OpenLayers. The reference tooling is a single Go binary ([`go-pmtiles`](https://github.com/protomaps/go-pmtiles), 635 stars) that converts, extracts, and uploads archives.

Three things make this genuinely different from a "just use a CDN" hack:

1. **Range-request delivery means any static host works.** A tile server needs special code; PMTiles needs a file server that supports HTTP Range — which is basically all of them, including the free tiers.
2. **The whole world fits in one file.** A full OpenStreetMap-based vector basemap is on the order of tens of gigabytes (or a few GB for lower zoom levels). One file you can `cp`, version, and back up.
3. **Zero per-load metering.** You pay for storage and bandwidth, not "loads." On Cloudflare R2, egress is free and storage is ~$0.015/GB/month — which is why "self-host maps for ~$5/mo" is a realistic headline, not marketing.

---

## The Stack: PMTiles + MapLibre + Cloudflare R2

The self-hosted map stack replaces the Mapbox stack one-for-one:

| Mapbox piece | Self-hosted replacement |
|---|---|
| Mapbox tile server / API | A **PMTiles file** on any static bucket |
| Mapbox GL JS (the renderer) | **[MapLibre GL JS](https://github.com/maplibre/maplibre-gl-js)** (12,000+ stars) — the open-source fork of the same renderer |
| Mapbox base styles | **[Protomaps Basemaps](https://github.com/protomaps/basemaps)** (776 stars) — open cartographic styles + PMTiles generation from OpenStreetMap |
| Mapbox vector tiles | **OpenMapTiles** schema (3,200+ stars) or Protomaps' own basemap build |

The renderer is the same lineage — MapLibre GL JS *is* Mapbox GL JS's open-source continuation, so if you've written Mapbox code, the migration is mostly a rename. And because PMTiles has a MapLibre plugin, the whole thing is a dozen lines of JavaScript.

---

## Step-by-Step: Self-Host a World Map

Here's the concrete path, sized for a Cloudflare Pages + R2 setup (but it works identically on S3, Bunny, or a homelab nginx box).

### 1. Get the data (a PMTiles file)

You have two choices: **generate it yourself** or **use a prebuilt basemap**.

**Use a prebuilt basemap (fastest).** Protomaps publishes ready-made OpenStreetMap-derived basemaps as PMTiles. You can grab one and upload it directly to your bucket — no generation step at all.

**Generate your own (full control).** Download the `pmtiles` binary from the [go-pmtiles releases](https://github.com/protomaps/go-pmtiles/releases), then convert from an MBTiles file (the format tools like [tippecanoe](https://github.com/felt/tippecanoe) produce):

```bash
pmtiles convert INPUT.mbtiles OUTPUT.pmtiles
pmtiles upload OUTPUT.pmtiles s3://my-bucket?region=us-east-1 \
  # requires AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY in env
```

For a full planet basemap you'd point Protomaps' [basemaps](https://github.com/protomaps/basemaps) pipeline at OpenStreetMap data and build the PMTiles yourself — heavier, but it's what gives you a Mapbox-quality basemap you own outright.

### 2. Host it (R2, S3, or any static server)

Upload the `.pmtiles` file to your bucket. That's it. The only requirement is **HTTP Range request support** — which R2, S3, Bunny, and nginx all provide. If you're on Cloudflare, R2 is the natural fit because **egress is free** (you pay only for storage and any Workers invocations), which is precisely why the per-load bill disappears.

### 3. Render it (MapLibre + the PMTiles plugin)

Point MapLibre GL JS (v1.15+) at the archive:

```js
import maplibregl from 'maplibre-gl';
import { Protocol } from 'pmtiles';

const protocol = new Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);

const map = new maplibregl.Map({
  container: 'map',
  style: {
    version: 8,
    sources: {
      basemap: {
        type: 'vector',
        url: 'pmtiles://https://your-bucket.example.com/world.pmtiles'
      }
    },
    layers: [ /* your style layers, or load a Protomaps Basemaps style */ ]
  }
});
```

That's the entire integration. `pmtiles://` tells MapLibre to fetch the archive and do the Range-request tile lookups for you. There's a [PMTiles viewer](https://pmtiles.io/) you can point at any archive to preview it before you write any code.

---

## What This Unlocks (and What It Doesn't)

**Where it shines:**

- **Dashboards and internal tools** — a homelab network map, a "where did I park" app, a family locator, a self-hosted asset tracker. Maps that would've been a Mapbox meter are now a file you already host.
- **Projects that might go viral** — the exact scenario where a per-load meter turns success into a bill. With PMTiles your marginal cost per additional user is *bandwidth*, not "loads."
- **Data you don't want in someone else's index** — location history, customer addresses, private infrastructure. It stays in your bucket.

**Honest limits:**

- **You own the ops.** No vendor to blame at 2 AM — you're the one who regenerates tiles when OpenStreetMap data changes. Protomaps makes this a periodic rebuild, not a daily chore, but it's real.
- **Geocoding is separate.** PMTiles handles *rendering* the map, not turning "123 Main St" into coordinates. That's still a Nominatim self-host or a paid geocoder — though that's a smaller, more predictable line item than per-load tile serving.
- **A full planet basemap is a big file.** Tens of GB at full zoom. For most projects you'll cap zoom or use a regional extract, which is a standard trade-off.

The throughline: **a map stopped being a vendor you rent and became a file you own.** The same way self-hosting replaced the SaaS analytics line item, the SaaS chat line item, and the SaaS "everything else" line item — now it takes the map too.

---

*Want the whole "kill the SaaS line item" playbook? Start with the [self-hosted app finder](https://devhandbook.io/self-hosted-stack-builder/) and see what else you can replace with a file and a container.*
