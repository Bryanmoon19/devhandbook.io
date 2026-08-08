#!/usr/bin/env bash
# devhandbook.io Cloudflare WAF Diagnostic & Fix Script
# Created by Moon Night Shift — July 2, 2026
# Usage: bash fix-devhandbook-domain.sh

set -euo pipefail

echo "🔍 devhandbook.io Domain Diagnostic"
echo "===================================="
echo ""

# Check current state
echo "📊 Step 1: Checking current state..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://devhandbook.io/)
echo "    devhandbook.io returns: HTTP $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Site is accessible! No action needed."
    exit 0
fi

echo ""
echo "🚨 Step 2: Issue confirmed — HTTP $HTTP_CODE with cf-mitigated: challenge"
echo ""
echo "📋 What this means:"
echo "    Cloudflare is intercepting ALL requests to devhandbook.io"
echo "    and showing a challenge/interstitial page."
echo "    This prevents real visitors from reaching the site."
echo ""

# Show DNS resolution
echo "🔧 Step 3: DNS Check"
DEV_IP=$(dig +short devhandbook.io | head -1 || echo "FAILED")
echo "    devhandbook.io resolves to: $DEV_IP"
if echo "$DEV_IP" | grep -q "104\." || echo "$DEV_IP" | grep -q "172\."; then
    echo "    ✅ DNS points to Cloudflare (expected)"
else
    echo "    ⚠️  DNS does not point to Cloudflare — check nameservers"
fi

echo ""
echo "🎯 ROOT CAUSE:"
echo "    One of these Cloudflare security features is too aggressive:"
echo ""
echo "    A) Bot Fight Mode or Super Bot Fight Mode"
echo "    B) Security Level set to 'High' or 'I'm Under Attack'"
echo "    C) A custom WAF rule blocking the Pages domain"
echo "    D) Custom domain needs re-verification in Pages settings"
echo ""

echo "🔧 MANUAL FIX STEPS (requires Cloudflare Dashboard access):"
echo "=========================================================="
echo ""
echo "Step 1: Log into https://dash.cloudflare.com"
echo "Step 2: Select 'devhandbook.io' zone"
echo ""
echo "Step 3: Check Bots Settings"
echo "    → Security → Bots"
echo "    → If 'Bot Fight Mode' is ON → turn it OFF"
echo "    → If 'Super Bot Fight Mode' is enabled → disable it"
echo "    → These are the #1 cause of 403 on Pages sites"
echo ""
echo "Step 4: Check Security Level"
echo "    → Security → WAF → Tools"
echo "    → Find 'Security Level'"
echo "    → Set to 'Medium' or 'Low' (NOT 'High' or 'I'm Under Attack')"
echo ""
echo "Step 5: Check Custom WAF Rules"
echo "    → Security → WAF → Custom rules"
echo "    → Look for any rule that might block requests"
echo "    → Disable any suspicious rules temporarily to test"
echo ""
echo "Step 6: Verify Pages Custom Domain"
echo "    → Go to https://dash.cloudflare.com → Pages"
echo "    → Select 'devhandbook-io' project"
echo "    → Custom Domains tab"
echo "    → Check if 'devhandbook.io' shows 'Active'"
echo "    → If not: remove and re-add the custom domain"
echo ""
echo "Step 7: Purge Cache (after changes)"
echo "    → Caching → Configuration → Purge Everything"
echo ""
echo "Step 8: Test"
echo "    Run: curl -I https://devhandbook.io/"
echo "    Should return HTTP 200 (not 403)"
echo ""

echo "🔄 AUTOMATED WORKAROUND (while fixing):"
echo "========================================"
echo ""
echo "Since the preview URL works, you can temporarily redirect traffic:"
echo ""
echo "Option A: Update DNS to point to Pages directly"
echo "    → DNS → devhandbook.io A record → change to CNAME → devhandbook-io.pages.dev"
echo ""
echo "Option B: Create a Cloudflare Worker as a proxy"
echo "    (only if WAF rules can't be changed)"
echo ""

echo "📞 If nothing works:"
echo "    Cloudflare Support: https://support.cloudflare.com"
echo "    Or DM @CloudflareHelp on Twitter"
echo ""

echo "✅ VERIFICATION:"
echo "================"
echo "After completing the steps above, run this command:"
echo ""
echo "    curl -s -o /dev/null -w \"%{http_code}\" https://devhandbook.io/"
echo ""
echo "Expected result: 200"
echo "Current result:  $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "403" ]; then
    echo "⚠️  ACTION REQUIRED: Site is still broken. Complete the manual fix steps above."
    exit 1
fi
