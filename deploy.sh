#!/bin/bash
set -e

OPSEC_SCANNER="$HOME/.openclaw/workspace/scripts/opsec-scan.sh"

# Run OPSEC scan first
if [ -f "$OPSEC_SCANNER" ]; then
  echo "🔒 Running OPSEC scan..."
  if ! bash "$OPSEC_SCANNER" .; then
    echo ""
    echo "❌ OPSEC scan found issues. Fix them before deploying."
    echo "   To skip (dangerous): SKIP_OPSEC=1 ./deploy.sh"
    [ "${SKIP_OPSEC:-0}" = "1" ] || exit 1
    echo "   ⚠️  Skipping OPSEC check (SKIP_OPSEC=1)"
  fi
  echo ""
fi

echo "🏗️  Building..."
npx eleventy
echo "🚀 Deploying..."
npx wrangler pages deploy _site --project-name=devhandbook-io
echo "✅ Done!"
