#!/bin/bash
# ============================================================
#  🔄 BotAssistant — Quick Rebuild (code changes only)
#  Use this after code changes that don't need PDF re-indexing
# ============================================================

set -e

echo ""
echo "🔄 Quick rebuild — deploying code changes..."
echo ""

# Rebuild and restart only changed services
docker compose build
docker compose up -d

echo ""
echo "✅ Deployment done! Services restarted with latest code."
echo ""
docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || docker compose ps
echo ""
