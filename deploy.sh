#!/bin/bash
set -e
echo "🏗️  Building..."
npx eleventy
echo "🚀 Deploying..."
npx wrangler pages deploy _site --project-name=devhandbook-io
echo "✅ Done!"
