---
layout: post.njk
title: "Self-Hosted Calendar Tools for Homelabbers: A Battle-Tested Guide"
date: 2026-06-26
description: "I spent months testing every self-hosted calendar option so you don't have to. Here's the honest truth about Radicale, Baïkal, Nextcloud, Home Assistant, Vikunja, and more — with real Docker configs and the gotchas nobody talks about."
tags: ["self-hosted", "calendar", "homelab", "docker", "nextcloud", "radicale", "baikal", "home-assistant", "vikunja"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-06-26-self-hosted-calendar-tools-homelab"
---

I've been running a homelab for years now — Proxmox, Docker containers, the whole nine yards. And somewhere along the way, I decided I was tired of Google Calendar knowing when my dentist appointments were. So I went looking for a self-hosted calendar solution that I could actually trust.

What I found was a fragmented landscape of tools that all *technically* work, but with wildly different trade-offs. Some are dead-simple CalDAV servers. Others are full-blown productivity suites. A few are technically calendar-capable but barely usable for the purpose. After months of testing, breaking things, migrating data, and cursing at sync conflicts, here's what I learned.

## What You're Actually Looking For

Before we dive into tools, let's be honest about what "self-hosted calendar" actually means. You might want:

- **Just CalDAV** — a dumb sync server that talks to Thunderbird, Apple Calendar, or DAVx⁵ on Android
- **A web UI** — because managing everything through a native client is limiting
- **Shared calendars** — family scheduling, project deadlines, team coordination
- **Reminders/notifications** — email, webhook, or push notifications for events
- **Calendar + tasks integration** — because who wants separate systems for "meeting at 3pm" and "fix the NAS by Friday"
- **Mobile sync** — and this is where the pain usually starts

My advice: be brutally honest about which of these you actually need. The more features you pile on, the more complex your solution becomes. I started wanting a web UI + tasks + shared calendars + mobile sync. I ended up with a CalDAV server and a separate task manager because the all-in-one solutions kept disappointing me in subtle but important ways.

## The Contenders

Here's what I actually tested, in the order I tried them:

### 1. Radicale — The "It Just Works" CalDAV Server

Radicale was my first stop, and honestly? If you just need CalDAV sync, this is probably where you should stop too.

Radicale is a small but complete CalDAV and CardDAV server written in Python. It's been around forever (since 2008), it's actively maintained, and it does exactly what it says on the tin: stores calendars and contacts, serves them via CalDAV/CardDAV, and doesn't try to be anything else.

**The good:**
- Zero configuration if you're okay with the defaults
- Lightweight — runs happily in 50MB RAM
- No database needed — stores everything as `.ics` and `.vcf` files in a directory
- Supports basic auth, LDAP, and even PAM authentication
- Built-in support for creating/editing events through a primitive web interface
- Handles shared calendars and multiple users
- Docker image is officially maintained and tiny

**The bad:**
- That web interface is *primitive* — think 2008-era basic HTML forms
- No recurring event UI in the web interface
- No email reminders built-in (you'd need to script something with cron + the files)
- The "no database" thing is a double-edged sword — a thousand events = a thousand files, and some filesystems don't love that
- No timezone intelligence beyond what the clients provide

**My Docker Compose setup:**

{% raw %}
```yaml
version: "3.8"

services:
  radicale:
    image: tomsquest/docker-radicale:latest
    container_name: radicale
    ports:
      - "5232:5232"
    volumes:
      - ./data:/data
      - ./config:/config:ro
    environment:
      - TAKE_FILE_OWNERSHIP=true
    restart: unless-stopped
```
{% endraw %}

And my minimal `config/config` file:

{% raw %}
```ini
[server]
hosts = 0.0.0.0:5232

[auth]
type = htpasswd
htpasswd_filename = /config/users
htpasswd_encryption = bcrypt

[storage]
filesystem_folder = /data/collections
```
{% endraw %}

I generated the htpasswd file with:

```bash
htpasswd -B -c config/users myusername
```

**Verdict:** I ran Radicale for about 6 months. It never crashed, sync was rock solid with Apple Calendar and Thunderbird, and DAVx⁵ on Android worked perfectly. The only reason I moved on was that I *really* wanted a decent web UI for creating events when I was on a computer without my usual calendar client.

### 2. Baïkal — A Step Up in Polish

Baïkal is another CalDAV/CardDAV server, but with a modern PHP-based web administration interface. Think of it as "Radicale with a nice coat of paint and a preferences panel."

It uses SQLite or MySQL for storage, has a clean admin dashboard for managing users and calendars, and the same solid CalDAV/CardDAV support you'd expect.

**The good:**
- Actual web admin interface that doesn't look like a CS student's first project
- SQLite or MySQL backend
- User and calendar management through the browser
- Still lightweight compared to the full-suite alternatives
- Good CalDAV compatibility — tested with all major clients

**The bad:**
- PHP. I know, I know — modern PHP is fine, but it's still PHP. You'll want to keep it updated.
- No built-in calendar *viewing* or editing in the web UI — the admin panel is for management only
- Still no reminders/notifications
- The project has had some maintenance gaps in the past (though it's active again now)
- Slightly more complex setup than Radicale

**My Docker Compose:**

{% raw %}
```yaml
version: "3.8"

services:
  baikal:
    image: ckulka/baikal:nginx
    container_name: baikal
    ports:
      - "8888:80"
    volumes:
      - ./config:/var/www/baikal/config
      - ./data:/var/www/baikal/Specific
    restart: unless-stopped
```
{% endraw %}

First run hits `http://your-server:8888` and walks you through database setup.

**Verdict:** I used Baïkal for about 3 months. The admin interface was genuinely nice for onboarding family members — I could create their accounts and shared calendars without editing config files. But at the end of the day, it was still just a CalDAV server with better ergonomics. The fundamental limitations (no web calendar view, no notifications) were the same as Radicale.

### 3. Nextcloud Calendar — The Kitchen Sink

Okay, here's where things get interesting. Nextcloud is a full collaboration platform — file storage, document editing, chat, and yes, a calendar app. If you're already running Nextcloud (or you've been looking for an excuse to), the Calendar app is genuinely good.

**The good:**
- Full web calendar with day/week/month views
- Drag-and-drop event creation
- Shared calendars with granular permissions
- Calendar sharing via public links
- Built-in reminders (web notifications and email)
- Recurring event support with a decent UI
- Integrates with Nextcloud Contacts and Tasks
- Mobile sync through DAVx⁵ works great
- The "it integrates with everything" factor

**The bad:**
- You're running *Nextcloud*. That's gigabytes of PHP, a database server, Redis, and all the attendant complexity.
- Resource-heavy compared to dedicated CalDAV servers
- Updates can be nerve-wracking — I've had Nextcloud major version upgrades go sideways
- The calendar app is good, but it's not the primary focus of the project
- Sometimes slow — that PHP + database stack isn't winning any speed contests
- Occasional CalDAV quirks with certain clients

**My Docker Compose (the full stack):**

{% raw %}
```yaml
version: "3.8"

services:
  nextcloud:
    image: nextcloud:30-apache
    container_name: nextcloud
    ports:
      - "8080:80"
    volumes:
      - ./nextcloud:/var/www/html
    environment:
      - MYSQL_PASSWORD=nextcloud_db_password
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
      - NEXTCLOUD_ADMIN_USER=admin
      - NEXTCLOUD_ADMIN_PASSWORD=your_admin_password
      - NEXTCLOUD_TRUSTED_DOMAINS=your-domain.com
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: mariadb:10.6
    container_name: nextcloud-db
    command: --transaction-isolation=READ-COMMITTED --log-bin=binlog --binlog-format=ROW
    volumes:
      - ./db:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_PASSWORD=nextcloud_db_password
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
    restart: unless-stopped

  redis:
    image: redis:alpine
    container_name: nextcloud-redis
    restart: unless-stopped

  cron:
    image: nextcloud:30-apache
    container_name: nextcloud-cron
    volumes:
      - ./nextcloud:/var/www/html:ro
    entrypoint: /cron.sh
    depends_on:
      - db
      - redis
    restart: unless-stopped
```
{% endraw %}

After first setup, you install the Calendar app from the app store, and you're off.

**Verdict:** I ran Nextcloud Calendar for about 4 months as part of a broader Nextcloud instance. It's genuinely the best web calendar experience in the self-hosted world. The problem was that I didn't actually *want* the rest of Nextcloud — I was paying the complexity cost of a full collaboration suite for a calendar and a handful of files. When a Nextcloud update broke my instance for an afternoon, I decided to simplify.

**Who it's for:** If you already run Nextcloud, or you want the full integrated experience (files + calendar + tasks + contacts + maybe Collabora), this is the obvious choice. Don't set up Nextcloud *just* for the calendar unless you hate yourself.

### 4. Vikunja — The Task Manager That Wants to Be a Calendar

Vikunja is primarily a task manager in the Todoist/Asana vein, but it has calendar views and CalDAV support. I was drawn to it because I wanted task + calendar integration without the Nextcloud bloat.

**The good:**
- Modern, fast web UI built with Vue.js
- Kanban boards, list views, AND calendar views for tasks
- CalDAV support for syncing with external calendar clients
- Labels, filters, namespaces
- API-first design
- Lightweight compared to Nextcloud
- Active development with regular releases

**The bad:**
- The CalDAV implementation is "beta" and it shows. I had sync issues with Apple Calendar.
- It's a task manager first, calendar second. The calendar view is tasks-on-a-calendar, not a traditional calendar.
- No recurring events in the calendar sense
- Migration path from other calendars is painful — CalDAV import had issues with recurring events
- The project is relatively young (though stable enough for daily use)

**My Docker Compose:**

{% raw %}
```yaml
version: "3.8"

services:
  vikunja:
    image: vikunja/vikunja:latest
    container_name: vikunja
    ports:
      - "3456:3456"
    volumes:
      - ./files:/app/vikunja/files
      - ./config.yml:/etc/vikunja/config.yml
    environment:
      - VIKUNJA_SERVICE_PUBLICURL=http://your-server:3456/
      - VIKUNJA_DATABASE_TYPE=sqlite
      - VIKUNJA_DATABASE_PATH=/app/vikunja/vikunja.db
    restart: unless-stopped
```
{% endraw %}

**Verdict:** I wanted to love Vikunja. The UI is genuinely beautiful, and if you're a task-oriented person (GTD methodology, project management), the calendar view might be enough. But as someone who gets invited to meetings and needs to put them on a calendar, the task-first approach was frustrating. The CalDAV issues were the nail in the coffin — I need reliable sync more than I need pretty Kanban boards.

**Who it's for:** Project managers, task-oriented people, anyone who thinks of their life as a series of projects with due dates rather than a schedule of events. If your "calendar" is mostly "things I need to do by Friday," Vikunja is worth a look.

### 5. Home Assistant Calendar — The Smart Home Angle

If you're deep into the smart home world, you already know Home Assistant. What you might not know is that it has a surprisingly capable calendar integration.

Home Assistant's calendar isn't a CalDAV server — it's more of a calendar *aggregator* and *display*. It can:
- Pull in external CalDAV calendars (including Radicale and Baïkal instances)
- Display them in the Lovelace UI
- Trigger automations based on calendar events ("turn on the porch light 30 minutes before the BBQ")
- Create local calendars that are stored in its database

**The good:**
- If you already run Home Assistant, it's "free"
- Automation integration is genuinely powerful
- Can aggregate multiple external calendars into one view
- Local calendars for storing schedules that trigger automations
- The family will actually look at it if you put it on a wall tablet

**The bad:**
- Not a standalone CalDAV server — you need something else for that
- The calendar editing UI is... basic
- No mobile sync directly — you'd sync the underlying CalDAV source
- Creating and managing calendars is YAML-heavy for advanced cases
- You're adding calendar management to your home automation platform, which is architecturally questionable

**Setting up a local calendar in Home Assistant:**

In your `configuration.yaml`:

{% raw %}
```yaml
calendar:
  - platform: local_calendar
    name: Home Schedule
```
{% endraw %}

And to connect to your Radicale/Baïkal instance:

{% raw %}
```yaml
calendar:
  - platform: caldav
    url: http://your-radicale:5232/user/calendar/
    username: !secret caldav_user
    password: !secret caldav_pass
```
{% endraw %}

**Verdict:** I use Home Assistant calendars for automation triggers, not for actual calendar management. "Turn on the holiday lights on December 1st" and "start preheating the house 45 minutes before my first meeting on weekdays" are genuinely useful automations. But I don't use HA as my primary calendar — that's what CalDAV servers are for.

**Who it's for:** Smart home enthusiasts who want their schedule to *do things*. Not a standalone calendar solution.

### 6. EteSync — If You Want End-to-End Encryption

I need to mention EteSync because it fills a niche that none of the others do: end-to-end encrypted calendar and contact sync.

If your threat model includes "I don't want my calendar data readable even if the server is compromised," EteSync is basically your only self-hosted option.

**The good:**
- True E2EE for calendars AND contacts
- Zero-knowledge server — the host can't read your data
- CalDAV bridge available for client compatibility
- Open source (though there's also a hosted paid option)
- Audited cryptography

**The bad:**
- More complex setup because of the encryption layer
- You'll need the CalDAV bridge for most clients, which is another moving part
- Smaller community than the others
- Performance overhead of encryption/decryption
- The self-hosted server is Rust-based, which is great, but documentation is sparser than the Python/PHP alternatives

**Who it's for:** Privacy purists, people with genuinely sensitive scheduling data (medical appointments, legal proceedings, etc.), or anyone who believes in defense-in-depth.

### 7. Honorable Mentions I Didn't Fully Test

- **sabre/dav** — The PHP library that Baïkal is built on. If you want to build something custom, start here.
- **DAViCal** — Another PHP CalDAV server. Older, more enterprise-oriented. I skipped it because Baïkal and Radicale covered my use cases.
- **InfCloud / CalDavZAP** — Web clients for CalDAV servers. You could pair these with Radicale for a full web experience. I didn't go down this route because it felt like duct tape.
- **Google Calendar/Outlook with CalDAV bridge** — You *can* sync Google Calendar to a CalDAV server using tools like `vdirsyncer`. I mention this only to say: if you're self-hosting because you don't trust Google, don't do this. It defeats the purpose.

## The Sync Problem (Or: Why Your Calendar Keeps Duplicating Events)

Here's the thing nobody tells you: CalDAV is a *protocol*, not a guarantee of perfect sync. I've had more frustrating hours debugging calendar sync issues than I'd like to admit.

**The recurring event problem:** Some clients handle recurring events differently. Apple Calendar and Thunderbird sometimes disagree about whether "every Monday" means "every Monday starting from the creation date" or "every Monday in the universe." When they sync through CalDAV, you can end up with duplicated, missing, or "occurrence exception" events that make no sense.

**The timezone problem:** This one bit me hard. I created an event at 2pm EST on my laptop, and it showed up as 11am PST on my phone. The server (Radicale) stored it correctly as UTC. The issue? DAVx⁵ on Android was defaulting to Pacific time because of some weird interaction with my work profile. I only noticed when I showed up three hours late to a meeting.

**The "which client owns the calendar" problem:** If you create calendars in Apple Calendar, some CalDAV servers handle the collection creation fine. Others don't. Radicale expects you to create calendars via its API or web UI, then subscribe to them. If you try to create a calendar from Apple Calendar pointing at Radicale, it... sort of works? Sometimes? It's undefined behavior.

**My advice:**
1. Pick ONE authoritative client for creating calendars and events
2. Use the others as read-only if possible
3. Test timezone behavior with a few throwaway events before committing your real schedule
4. Set up automated backups of your `.ics` files (if using file-based storage) or database dumps (if using database storage)
5. Don't trust CalDAV for mission-critical scheduling without testing your specific client combination

## My Current Setup (After All This Testing)

Here's what I'm actually running in production today, after all the experiments:

**CalDAV server:** Radicale
**Why:** It never breaks. It's boring technology in the best way possible. My calendars sync reliably between my devices, and I don't have to think about it.

**Web UI:** I don't use one. If I need to create an event from a browser, I use Thunderbird's calendar view or temporarily open Apple Calendar through my Mac's screen sharing.

**Tasks:** Vikunja (I know, I know — after all that criticism. I run it separately for task management, and I don't try to sync its calendar view anywhere. It's just for tasks.)

**Home Assistant:** Connected to Radicale via CalDAV integration for automation triggers.

**Backups:** Weekly `tar` of the Radicale data directory to my NAS, plus Restic snapshots to Backblaze B2.

**Mobile:** DAVx⁵ on Android (configured to ignore my work profile's timezone nonsense), native Apple Calendar on iOS.

Is it perfect? No. Do I sometimes miss the polish of Google Calendar's web interface? Absolutely. But my data is mine, sync is reliable, and nothing breaks on update day.

## The Decision Matrix

Here's my honest attempt at mapping use cases to tools:

| You want... | Consider |
|-------------|----------|
| Dead-simple CalDAV that never breaks | **Radicale** |
| CalDAV with a nice admin panel | **Baïkal** |
| Full web calendar + reminders + sharing | **Nextcloud Calendar** |
| Task-first with calendar view | **Vikunja** |
| Calendar-triggered smart home automations | **Home Assistant** + CalDAV source |
| Maximum privacy / E2EE | **EteSync** |
| Already running Nextcloud | **Nextcloud Calendar** (obviously) |

## Final Thoughts

The self-hosted calendar landscape is simultaneously better and worse than you'd expect. Better because there are genuine options that work. Worse because none of them are as polished as the proprietary alternatives, and the gap is most noticeable in the details: recurring event UIs, timezone handling, mobile notification reliability.

My advice to homelabbers looking for calendar solutions:

**Start simple.** Run Radicale. See if a basic CalDAV server meets your needs. It probably will, and you'll save yourself months of complexity.

**Add complexity only when you hit a wall.** Don't start with Nextcloud because you *might* want file sharing someday. Start with the calendar, and migrate up when you actually need more.

**Test your sync stack thoroughly.** Create recurring events, move them, delete single occurrences, check timezone behavior across devices. Do this *before* you migrate your real calendar.

**Have a backup strategy.** Calendar data is ephemeral until it's not. That one appointment reminder might be the difference between showing up for your kid's recital or not.

The dream of a truly open, self-hosted, feature-complete calendar ecosystem isn't quite here yet. But for most of us, "good enough" is just a `docker-compose up` away. And honestly? "Good enough, and I own my data" beats "perfect, and Google owns a copy" most days of the week.

---

*If you found this useful, you might also like my post on [self-hosted contacts and CardDAV](/blog/2026-06-10-self-hosted-contacts-carddav) (spoiler: just use Radicale for that too).*
