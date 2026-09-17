#!/usr/bin/env python3
"""
Generate the "Sovereign Finance Stack" free lead-magnet PDF.

A practical, honest guide: run your own money tools (budget + receipt
parsing + auto-categorization) with self-hosted, local-AI infrastructure.
Written from the unique banker x homelabber vantage point.

Output: _site/sovereign-stack/sovereign-stack-guide.pdf
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable,
    ListItem, Preformatted, HRFlowable, Table, TableStyle,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "_site", "sovereign-stack")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "sovereign-stack-guide.pdf")

# ---- palette ----
NAVY = colors.HexColor("#0f172a")
TEAL = colors.HexColor("#14b8a6")
SLATE = colors.HexColor("#475569")
LIGHT = colors.HexColor("#f1f5f9")
ACCENT = colors.HexColor("#0ea5e9")

styles = getSampleStyleSheet()

title_st = ParagraphStyle("TitleX", parent=styles["Title"], textColor=NAVY,
                          fontSize=26, leading=32, spaceAfter=6)
sub_st = ParagraphStyle("SubX", parent=styles["Normal"], textColor=SLATE,
                        fontSize=12, leading=17, spaceAfter=18)
h1 = ParagraphStyle("H1X", parent=styles["Heading1"], textColor=NAVY,
                    fontSize=17, leading=22, spaceBefore=16, spaceAfter=8)
h2 = ParagraphStyle("H2X", parent=styles["Heading2"], textColor=TEAL,
                    fontSize=13, leading=17, spaceBefore=10, spaceAfter=5)
body = ParagraphStyle("BodyX", parent=styles["Normal"], textColor=NAVY,
                      fontSize=10.5, leading=16, spaceAfter=8)
bullet = ParagraphStyle("BulletX", parent=body, leftIndent=16, spaceAfter=4)
code = ParagraphStyle("CodeX", parent=styles["Code"], fontSize=8.5,
                      leading=12, backColor=LIGHT, borderColor=colors.HexColor("#e2e8f0"),
                      borderWidth=0.6, borderPadding=6, textColor=NAVY)
small = ParagraphStyle("SmallX", parent=body, fontSize=8.5, textColor=SLATE)
caption = ParagraphStyle("CapX", parent=body, fontSize=9, textColor=SLATE,
                         alignment=TA_CENTER, spaceBefore=4)

def P(t, s=body): return Paragraph(t, s)
def B(t): return Paragraph(t, bullet)
def C(t): return Preformatted(t, code)

def bullet_list(items):
    return ListFlowable([ListItem(Paragraph(i, bullet), leftIndent=18)
                         for i in items], bulletType="bullet", start="•")

def divider():
    return HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#e2e8f0"),
                      spaceBefore=6, spaceAfter=6)

story = []

# ============================ COVER ============================
story.append(Spacer(1, 1.2 * inch))
story.append(Paragraph("The Sovereign Finance Stack", title_st))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Run your own money tools — budgeting, receipt parsing, and automatic "
    "categorization — on infrastructure you control, with a local AI that never "
    "sees your data.", sub_st))
story.append(Spacer(1, 0.4 * inch))
story.append(HRFlowable(width="40%", thickness=1.4, color=TEAL, hAlign="LEFT"))
story.append(Spacer(1, 0.35 * inch))
story.append(P("A practical field guide by devhandbook.io", small))
story.append(P("Written from the unusual seat of a personal banker who also runs a homelab.", small))
story.append(Spacer(1, 0.5 * inch))
story.append(P("<b>What's inside</b>", body))
story.append(bullet_list([
    "Why the smart move in 2026 is self-hosting your finances",
    "The three-layer stack, explained plainly",
    "A working Docker Compose setup you can paste and run",
    "Receipt parsing with a local LLM — nothing leaves your machine",
    "Backups and security hardening a banker actually trusts",
    "The one habit that matters more than any tool",
]))
story.append(PageBreak())

# ============================ WHY ============================
story.append(P("1 · Why self-host your money", h1))
story.append(P(
    "For a long time the default answer to personal finance software was a "
    "subscription app — a YNAB or a Mint (RIP) or a cloud budgeting tool that "
    "connects to your bank through a third party. Those tools are genuinely good "
    "at what they do. But three things changed the math:"))
story.append(bullet_list([
    "<b>Price fatigue.</b> Subscription fees compound. A $15/mo budgeting app is "
    "$180/yr, every year, forever — for features that mostly amount to a spreadsheet "
    "with good categorization.",
    "<b>Privacy.</b> Cloud budgeting means your transaction history — every purchase, "
    "every merchant, every recurring bill — lives on someone else's server, usually "
    "connected through a data aggregator like Plaid. You don't own that copy.",
    "<b>Local AI got good, and cheap.</b> You can now run a capable language model on "
    "a modest home machine to read a receipt, guess a category, and file it — with zero "
    "data leaving your network.",
]))
story.append(P(
    "The result is a real alternative: a <b>sovereign stack</b> you own, that costs "
    "nothing monthly, and that your data never leaves. This guide walks you through it."))

story.append(P("A note on who this is for", h2))
story.append(P(
    "You don't need to be a developer. If you can copy a config file, run a Docker "
    "command, and follow a checklist, you can do this. Everything below runs on a "
    "$100 mini PC, an old laptop, or a NAS you already own."))
story.append(PageBreak())

# ============================ THE STACK ============================
story.append(P("2 · The three-layer stack", h1))
story.append(P("Three moving parts, each with a clear job:"))
story.append(bullet_list([
    "<b>Layer 1 — The ledger.</b> A self-hosted budgeting app that stores your "
    "accounts, categories, and transactions. It's the source of truth.",
    "<b>Layer 2 — The brain.</b> A local language model (via Ollama) that reads raw "
    "text — a receipt, an emailed invoice, a pasted bank export — and turns it into "
    "a categorized transaction.",
    "<b>Layer 3 — The glue.</b> A small script or automation that shuttles parsed "
    "transactions into the ledger and runs on a schedule.",
]))
story.append(Spacer(1, 4))
story.append(P("<b>The ledger — your two best options</b>", h2))
story.append(P("<b>Actual Budget</b> — the closest self-hosted cousin to YNAB. "
               "Envelope budgeting, a clean web UI, first-class mobile apps, and a "
               "built-in importer that migrates YNAB4 data. Runs as a single Node app "
               "in Docker.", body))
story.append(P("<b>Firefly III</b> — more of a double-entry bookkeeping tool. More "
               "powerful for reporting and multi-currency, a little more to learn. Has "
               "a separate Data Importer that accepts CSV/bank exports. Runs in Docker.", body))
story.append(P("Both are free, open-source, and actively maintained. Pick Actual if you "
               "want YNAB-style budgeting; pick Firefly if you want closer-to-bookkeeping "
               "reporting. This guide uses Actual Budget for the examples."))
story.append(PageBreak())

# ============================ DOCKER COMPOSE ============================
story.append(P("3 · A working Docker Compose setup", h1))
story.append(P("Create a folder and paste this into <b>docker-compose.yml</b>:"))
story.append(C(
"""version: "3"
services:
  actual:
    image: actualbudget/actual-server:latest
    container_name: actual-budget
    restart: unless-stopped
    ports:
      - "5006:5006"
    volumes:
      - ./actual-data:/data

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ./ollama-data:/root/.ollama
"""))
story.append(P("Then bring it up:"))
story.append(C(
"""docker compose up -d
# pull a small, capable local model for receipt work
docker exec -it ollama ollama pull qwen2.5:7b
"""))
story.append(P(
    "Visit <b>http://localhost:5006</b>, create your budget, and add your accounts. "
    "You now have a real ledger running on your own hardware. No subscription, no "
    "cloud, no Plaid."))
story.append(Spacer(1, 4))
story.append(P("A word on models", h2))
story.append(P(
    "For receipt and categorization work you don't need the biggest model — you need "
    "one that follows a simple instruction reliably and runs fast on modest hardware. "
    "7B-class models like <b>qwen2.5:7b</b> or <b>llama3.1:8b</b> are the sweet spot. "
    "If you have a beefier machine, step up to a 14B or 32B for noticeably better "
    "handwriting and OCR on messy receipts."))
story.append(PageBreak())

# ============================ RECEIPT PARSING ============================
story.append(P("4 · Receipt parsing with a local LLM", h1))
story.append(P(
    "This is the part that feels like magic. You feed a raw receipt (or a screenshot "
    "of one) to a local model and ask it to return structured data — merchant, date, "
    "total, and a suggested category. Because the model runs locally through Ollama, "
    "the receipt never leaves your network."))
story.append(P("Here's the core of a working parser (Python, using the Ollama HTTP API):"))
story.append(C(
'''import json, requests

def parse_receipt(text: str) -> dict:
    prompt = (
        "You are a bookkeeping assistant. Given the receipt text below, "
        "return JSON with keys: merchant, date (YYYY-MM-DD), total (number), "
        "and category (one of: Groceries, Dining, Transport, Utilities, "
        "Shopping, Health, Entertainment, Other).\\n\\nReceipt:\\n" + text
    )
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False,
    })
    return json.loads(r.json()["response"])
'''))
story.append(P(
    "For images (a photo of a paper receipt), pair this with a lightweight OCR step "
    "first, or use a vision-capable local model. The pattern is the same: local model, "
    "structured output, then file it into your ledger."))
story.append(Spacer(1, 4))
story.append(P("Auto-categorization", h2))
story.append(P(
    "Once you've categorized a few dozen transactions, you can let the local model "
    "suggest categories for new ones automatically. Feed it the merchant and a short "
    "description, plus your category list, and let it return the best match. Review "
    "its guesses — the point is to save keystrokes, not to go on autopilot with your "
    "books. <b>You remain the auditor.</b>"))
story.append(PageBreak())

# ============================ BACKUPS + SECURITY ============================
story.append(P("5 · Backups and security a banker trusts", h1))
story.append(P("The rule from my day job applies at home too: <b>if you don't have a "
               "backup you can actually restore from, you don't have a backup.</b>"))
story.append(P("<b>Backups — the 3-2-1 rule</b>", h2))
story.append(bullet_list([
    "<b>3</b> copies of your ledger data",
    "<b>2</b> different media (e.g. the server disk + a NAS or external drive)",
    "<b>1</b> copy offsite (a second location, or an encrypted cloud upload)",
]))
story.append(P("For Actual Budget, the entire <b>/data</b> folder is your backup. A "
               "nightly copy of that folder to a second machine — and a weekly copy "
               "offsite — covers you. Test the restore: copy it to a fresh container "
               "and confirm it loads."))
story.append(P("<b>Security hardening</b>", h2))
story.append(bullet_list([
    "<b>Keep it off the public internet.</b> Run the stack on your home network. If you "
    "want remote access, use a VPN (WireGuard or Tailscale) — not a forwarded port.",
    "<b>Strong auth.</b> Use a long, unique password (a password manager is non-negotiable "
    "here) and enable any available 2FA.",
    "<b>Least privilege.</b> Your finance stack doesn't need to run as root or share a "
    "network with random IoT devices. Segment it.",
    "<b>Patch it.</b> Docker images get security fixes. A monthly `docker compose pull` "
    "and restart is a cheap habit.",
]))
story.append(PageBreak())

# ============================ THE HABIT ============================
story.append(P("6 · The one habit that matters more than any tool", h1))
story.append(P(
    "None of this replaces the actual work of looking at your money. The tool makes it "
    "painless; the habit makes it work. The single highest-leverage practice in personal "
    "finance is a <b>weekly 15-minute review</b>: reconcile your transactions, glance at "
    "your category totals, and notice anything that drifted."))
story.append(bullet_list([
    "<b>Sunday, 15 minutes.</b> Same time, every week. Habit beats willpower.",
    "<b>Reconcile.</b> Make sure what's in your ledger matches what's in your accounts.",
    "<b>One question.</b> 'Did I spend in line with what I actually care about this week?' "
    "That's it. No guilt, just awareness.",
]))
story.append(P(
    "The sobering part of my job is seeing how many people simply never look. The "
    "person who checks once a week — with any tool, even a spreadsheet — is already "
    "ahead of most of the population. A sovereign stack just makes that check fast, "
    "private, and free."))
story.append(PageBreak())

# ============================ NEXT STEPS ============================
story.append(P("What's next", h1))
story.append(P(
    "This guide is the free introduction. If it's useful, more is on the way — deeper "
    "walkthroughs on wiring the parser into Actual Budget, turning the whole thing into "
    "a scheduled automation, and building the same kind of stack for a small business."))
story.append(Spacer(1, 8))
story.append(P("Thanks for reading. — the person behind devhandbook.io", caption))
story.append(Spacer(1, 0.2 * inch))
story.append(P("devhandbook.io · The Sovereign Finance Stack", small))
story.append(P("No tracking, no upsell required, your email stays with us.", small))

doc = SimpleDocTemplate(OUT_PATH, pagesize=letter,
                        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                        title="The Sovereign Finance Stack",
                        author="devhandbook.io")

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE)
    canvas.drawCentredString(letter[0] / 2, 0.4 * inch,
                             "The Sovereign Finance Stack · devhandbook.io")
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("Wrote", OUT_PATH)
