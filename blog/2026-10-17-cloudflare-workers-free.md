# Cloudflare Workers: Build Serverless Tools for Free

*Run code at the edge, in 200+ cities, without managing servers. And yes, the free tier is actually useful.*

---

## Introduction

Cloudflare Workers let you run JavaScript, TypeScript, Rust, or Python code on Cloudflare's global edge network — the same infrastructure that handles 20%+ of the internet's traffic. Instead of deploying to a single region and routing every request there, your code runs in data centers scattered across the globe, milliseconds away from your users.

The magic is simple: you write a small script, deploy it with a CLI tool called Wrangler, and it runs instantly on every request that hits your domain. No containers to manage. No "cold starts" that take 2 seconds to spin up. No server patching at 3 AM.

Cloudflare offers a **generous free tier** — 100,000 requests per day, 10ms of CPU time per request, and access to the full Workers ecosystem including KV storage, D1 databases, R2 object storage, and even AI inference. For side projects, prototypes, and small production tools, that's more than enough to get real work done without spending a dime.

This guide covers everything from your first "Hello World" to real-world patterns like API proxies, URL shorteners, and AI inference at the edge. Let's build something.

---

## Free Tier: What's Actually Included

Before we write code, let's be honest about the limits so you know what you're working with.

| Feature | Free Tier |
|---------|-----------|
| **Requests/day** | 100,000 |
| **CPU time/request** | 10ms |
| **Worker scripts** | 100 |
| **Memory** | 128MB |
| **KV reads/day** | 100,000 |
| **D1 reads/day** | 5 million |
| **R2 storage** | 10 GB |
| **Workers AI requests** | 100,000/day |

**100,000 requests/day** means roughly 3 million requests per month. That's not hobby-project territory — that's small-to-medium production app territory. A URL shortener, a lightweight API gateway, or an A/B testing service can comfortably live on the free tier.

The **10ms CPU limit** is the real constraint. This is *CPU time*, not total request time. Waiting on a fetch to an external API doesn't count toward this limit. But heavy computation — JSON parsing, encryption, image manipulation — burns through it fast. Keep workers lean and delegate heavy lifting to services designed for it.

---

## Setting Up Your First Worker

### Install Wrangler

Cloudflare's CLI tool is called Wrangler. Install it globally via npm:

```bash
npm install -g wrangler
```

Authenticate with your Cloudflare account:

```bash
wrangler login
```

This opens a browser window, authorizes Wrangler, and saves credentials locally. You'll need a Cloudflare account, but you don't need a domain on Cloudflare to use Workers.

### Hello World

Create a new project:

```bash
wrangler init my-first-worker
cd my-first-worker
```

Select "Yes" when it asks to create a TypeScript worker. Wrangler scaffolds a basic project with `src/index.ts`:

```typescript
export interface Env {
  // Bindings go here (KV, D1, R2, etc.)
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return new Response("Hello World!");
  },
};
```

The `fetch` handler is the entry point for HTTP requests. Every worker must export a default object with a `fetch` method that returns a `Response`. The `Env` interface holds your bindings (databases, storage buckets, secrets), and `ExecutionContext` lets you schedule work after returning a response via `ctx.waitUntil()`.

Test locally:

```bash
wrangler dev
```

Open `http://localhost:8787` in your browser. You should see "Hello World!"

### Deploy

One command pushes to production:

```bash
wrangler deploy
```

Your worker gets a URL like `https://my-first-worker.your-account.workers.dev`. Live on Cloudflare's edge network in under a minute.

---

## Real-World Use Cases

### 1. API Proxy / Gateway

Need to add authentication, rate limiting, or logging to an existing API without touching the original service? Put a Worker in front.

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Add an API key check
    const apiKey = request.headers.get("X-API-Key");
    if (apiKey !== env.API_SECRET) {
      return new Response("Unauthorized", { status: 401 });
    }

    // Strip the original host header, forward the rest
    const url = new URL(request.url);
    const target = new URL(url.pathname + url.search, "https://api.upstream-service.com");

    const modified = new Request(target, request);
    modified.headers.delete("X-API-Key"); // don't leak our secret

    return fetch(modified);
  },
};
```

Add rate limiting with KV:

```typescript
async function checkRateLimit(clientId: string, env: Env): Promise<boolean> {
  const key = `rate:${clientId}`;
  const current = parseInt((await env.RATE_LIMIT_KV.get(key)) || "0");

  if (current > 100) return false; // 100 requests per minute

  await env.RATE_LIMIT_KV.put(key, String(current + 1), { expirationTtl: 60 });
  return true;
}
```

### 2. URL Shortener

A minimal URL shortener using KV storage:

```typescript
export interface Env {
  URLS: KVNamespace;
}

function generateSlug(): string {
  return Math.random().toString(36).substring(2, 8);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // POST /create → store URL, return slug
    if (request.method === "POST" && url.pathname === "/create") {
      const { longUrl } = await request.json<{ longUrl: string }>();
      const slug = generateSlug();
      await env.URLS.put(slug, longUrl, { expirationTtl: 86400 * 30 }); // 30 days
      return Response.json({ shortUrl: `https://${url.host}/${slug}` });
    }

    // GET /:slug → redirect
    const slug = url.pathname.slice(1);
    const longUrl = await env.URLS.get(slug);
    if (longUrl) {
      return Response.redirect(longUrl, 301);
    }

    return new Response("Not found", { status: 404 });
  },
};
```

Deploy this and you have a working URL shortener with global edge caching, zero cold starts, and 100k free requests per day. Not bad for 30 lines of code.

### 3. Image Optimization

Use Workers to resize, format-convert, or add watermarks to images on the fly. Combine with Cloudflare Images or R2 for storage:

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const imageUrl = url.searchParams.get("url");
    const width = url.searchParams.get("w") || "800";

    if (!imageUrl) return new Response("Missing url param", { status: 400 });

    // Fetch original image
    const response = await fetch(imageUrl);
    if (!response.ok) return new Response("Failed to fetch image", { status: 502 });

    // Use Cloudflare's Image Resizing (available on paid plans)
    // Or process with a library like @cf-wasm/photon on free tier
    const image = await response.arrayBuffer();

    // Return with appropriate cache headers
    return new Response(image, {
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "image/jpeg",
        "Cache-Control": "public, max-age=31536000",
      },
    });
  },
};
```

For actual image manipulation on the free tier, check out `@cf-wasm/photon` — a WebAssembly-based image processing library that runs inside Workers.

### 4. A/B Testing

Route users to different versions of your site based on a cookie or random assignment:

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const cookie = request.headers.get("Cookie") || "";
    let variant = cookie.match(/variant=(\w)/)?.[1];

    if (!variant) {
      variant = Math.random() < 0.5 ? "a" : "b";
    }

    url.hostname = variant === "a" ? "origin-site.com" : "new-site.com";

    const response = await fetch(url.toString(), request);
    const modified = new Response(response.body, response);
    modified.headers.append("Set-Cookie", `variant=${variant}; Path=/; Max-Age=86400`);

    return modified;
  },
};
```

Track the results by logging the variant assignment to your analytics platform or a D1 database.

### 5. Geolocation Redirect

Cloudflare injects `CF-IPCountry` and other geolocation headers into every request. Use them to route users to localized content:

```typescript
export default {
  async fetch(request: Request): Promise<Response> {
    const country = request.headers.get("CF-IPCountry") || "US";
    const url = new URL(request.url);

    const localizedHosts: Record<string, string> = {
      DE: "de.example.com",
      FR: "fr.example.com",
      JP: "jp.example.com",
    };

    url.hostname = localizedHosts[country] || "www.example.com";
    return fetch(url.toString(), request);
  },
};
```

No external geolocation API needed. It's already in the request headers, added by Cloudflare at the edge.

---

## Workers + KV Storage

KV (Key-Value) is Cloudflare's global, eventually-consistent data store. It's perfect for configuration, feature flags, session data, and cached content.

### Creating a KV Namespace

```bash
wrangler kv:namespace create "MY_KV"
```

Add the binding to your `wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "MY_KV"
id = "your-namespace-id"
```

### Basic Operations

```typescript
export interface Env {
  MY_KV: KVNamespace;
}

// Write
await env.MY_KV.put("key", "value", { expirationTtl: 3600 }); // expires in 1 hour

// Read
const value = await env.MY_KV.get("key");

// Read with metadata
const result = await env.MY_KV.getWithMetadata("key");
console.log(result.value, result.metadata);

// List keys
const list = await env.MY_KV.list({ prefix: "user:", limit: 10 });
```

**Important:** KV is eventually consistent. Writes may take up to 60 seconds to propagate globally. For strongly consistent reads, use D1 instead.

---

## Workers + D1 Database (SQLite at the Edge)

D1 is Cloudflare's serverless SQLite database. If you know SQL, you already know D1. It's perfect for relational data, user accounts, content management, and anything that needs ACID transactions.

### Setting Up D1

Create a database:

```bash
wrangler d1 create my-database
```

Add to `wrangler.toml`:

```toml
[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "your-database-id"
```

### Running Migrations

```bash
wrangler d1 execute my-database --file=./schema.sql
```

Example schema:

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Querying from a Worker

```typescript
export interface Env {
  DB: D1Database;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Insert a user
    await env.DB.prepare("INSERT INTO users (email) VALUES (?)")
      .bind("user@example.com")
      .run();

    // Fetch users
    const { results } = await env.DB.prepare("SELECT * FROM users LIMIT 10").all();

    return Response.json(results);
  },
};
```

D1 supports parameterized queries, transactions, and even batch operations. It's SQLite, so full-text search, JSON functions, and window functions all work.

---

## Workers + R2 Storage (S3-Compatible)

R2 is Cloudflare's object storage service. It's S3-compatible but with zero egress fees — you only pay for storage and operations, not for bandwidth. This makes it dramatically cheaper than AWS S3 for serving files to users.

### Uploading Files

```typescript
export interface Env {
  MY_BUCKET: R2Bucket;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "PUT") {
      const key = url.pathname.slice(1);
      await env.MY_BUCKET.put(key, request.body);
      return new Response("Uploaded", { status: 201 });
    }

    if (request.method === "GET") {
      const key = url.pathname.slice(1);
      const object = await env.MY_BUCKET.get(key);
      if (!object) return new Response("Not found", { status: 404 });

      return new Response(object.body, {
        headers: {
          "Content-Type": object.httpMetadata?.contentType || "application/octet-stream",
        },
      });
    }

    return new Response("Method not allowed", { status: 405 });
  },
};
```

R2 is ideal for user uploads, backups, static assets, and media storage. Combined with Workers, you can build entire content pipelines — upload, process, serve — without touching a traditional server.

---

## Workers AI: ML at the Edge

Cloudflare Workers AI lets you run machine learning models directly on the edge. No API keys for OpenAI, no network latency to external services. The model runs in the same data center handling your request.

### Available Models

Workers AI includes models for:
- **Text generation** (Llama, Mistral, Gemma)
- **Embeddings** (for search and similarity)
- **Image classification**
- **Translation**
- **Summarization**
- **Sentiment analysis**

### Using Workers AI

```typescript
export interface Env {
  AI: Ai;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { prompt } = await request.json<{ prompt: string }>();

    const response = await env.AI.run("@cf/meta/llama-2-7b-chat-int8", {
      messages: [
        { role: "system", content: "You are a helpful assistant." },
        { role: "user", content: prompt },
      ],
    });

    return Response.json(response);
  },
};
```

Free tier includes **100,000 AI requests per day**. That's enough to experiment heavily or run a small production AI feature without paying for external APIs.

**Note:** The free tier has limits on model sizes and concurrent requests. For heavy AI workloads, the paid tier scales better.

---

## Comparison with Alternatives

| Feature | Cloudflare Workers | Vercel Edge | Deno Deploy | Fly.io |
|---------|-------------------|-------------|-------------|--------|
| **Free requests** | 100K/day | 1M/month (Vercel) | 1M/month | None (credits) |
| **Cold starts** | None | None | None | ~300ms |
| **Languages** | JS/TS, Rust, Python | JS/TS | JS/TS, Python | Anything (Docker) |
| **Edge locations** | 300+ | 100+ | 35 | 30+ |
| **Built-in storage** | KV, D1, R2 | Vercel KV, Postgres | Deno KV | Postgres, S3 |
| **Egress fees** | $0 (R2) | $0 (Vercel) | $0 | $0 |
| **WASM support** | Yes | Limited | Yes | Yes |

**Vercel Edge** is great if you're already in the Next.js ecosystem. The integration is seamless. But you're locked into their platform conventions.

**Deno Deploy** offers a cleaner runtime (no Node.js baggage) and built-in TypeScript. The ecosystem is smaller but growing fast.

**Fly.io** gives you full Docker containers running globally. More flexibility, more complexity, and cold starts exist. Best for stateful services or when you need a full Linux environment.

**Cloudflare Workers** wins on edge coverage, integration breadth (KV/D1/R2/AI all under one roof), and the sheer generosity of the free tier.

---

## Pricing Breakdown

### Free Tier
- 100,000 requests/day
- 10ms CPU/request
- 100 Workers scripts
- 1GB KV storage
- 5M D1 reads/day
- 10GB R2 storage
- 100K AI requests/day

### Paid Tier (Workers Paid)
- $0.30 per million requests
- 50ms CPU/request limit
- Unlimited Workers scripts
- Workers KV: $0.50/GB-month
- D1: $5/month base + usage
- R2: $0.015/GB-month storage, $0.0045/million operations
- Workers AI: $0.011 per 1K tokens (varies by model)

For context: a site doing 1 million requests per month costs about **$0.30** on Workers. The free tier handles 3 million requests per month. Unless you're running a high-traffic production service, you may never need to pay.

---

## Limitations and Workarounds

### 10ms CPU Time

The free tier's 10ms CPU limit is the biggest constraint. Strategies to work within it:

- **Offload heavy work:** Use Durable Objects (paid) for stateful coordination, or call external APIs for heavy computation.
- **Cache aggressively:** Cache API responses at the edge to avoid repeated computation.
- **Use WASM:** Rust-compiled WASM often outperforms JavaScript for CPU-bound tasks.
- **Stream responses:** For large payloads, stream data instead of buffering it all in memory.

### No Native WebSocket Server

Workers can *receive* WebSocket connections via Durable Objects, but free tier has limited Durable Object usage. For real-time features, consider:
- Cloudflare Durable Objects (paid, but cheap)
- External services like Pusher or Ably
- Server-Sent Events (SSE) over HTTP, which Workers handle natively

### Environment Differences

The Workers runtime is not Node.js. Some npm packages won't work because they depend on Node APIs like `fs`, `crypto` (legacy), or `http`. Solutions:
- Use `wrangler.toml` compatibility flags
- Prefer `fetch` over `http`
- Use Web Crypto API instead of Node's `crypto`
- Check package compatibility at [workers.cloudflare.com/works](https://workers.cloudflare.com/works)

### Cold Starts Don't Exist, But...

Workers don't have cold starts in the traditional sense. However, if you import massive dependencies or initialize large data structures at the top level, the *script initialization* can add latency. Keep top-level code minimal and lazy-load heavy modules inside the `fetch` handler.

---

## Conclusion

Cloudflare Workers represents a genuinely useful free tier in a space where "free" often means "useless demo." 100,000 requests per day with edge deployment, KV storage, SQLite databases, object storage, and AI inference is enough to build and run real tools.

The patterns covered here — API proxies, URL shorteners, image optimization, A/B testing, geolocation routing, and AI features — are just scratching the surface. Combined with R2's zero-egress object storage and D1's familiar SQLite interface, you can build full-stack applications that scale globally without managing servers or sweating the bill.

If you've been on the fence about serverless because of cost or complexity, Workers is the place to start. Write the code, run `wrangler deploy`, and your tool is live in 200+ cities worldwide.

---

## Further Reading

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [Workers KV Documentation](https://developers.cloudflare.com/kv/)
- [D1 Database Guide](https://developers.cloudflare.com/d1/)
- [R2 Object Storage](https://developers.cloudflare.com/r2/)
- [Workers AI Models](https://developers.cloudflare.com/workers-ai/models/)
- [Awesome Cloudflare Workers (Community)](https://github.com/cloudflare/awesome-cloudflare-workers)

---

*Built something cool with Workers? The devhandbook.io community wants to hear about it.*
