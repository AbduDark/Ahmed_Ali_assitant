#!/bin/bash
# ============================================================
#  🚀 BotAssistant — Server Deploy Script
#  Builds, deploys, and initializes everything in one shot
# ============================================================

set -e  # Exit on any error

echo ""
echo "============================================================"
echo "  🚀 BotAssistant — Full Server Deployment"
echo "  📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""

# ── Step 0: Check prerequisites ────────────────────────────────
echo "🔍 [0/5] Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose V2 is not available. Please update Docker."
    exit 1
fi

# Check PDF files exist
if [ ! -f "EgyptianHistory-Ar-EB-part1.pdf" ]; then
    echo "⚠️  Warning: EgyptianHistory-Ar-EB-part1.pdf not found in project root"
fi
if [ ! -f "EgyptianHistory-Ar-EB-part2.pdf" ]; then
    echo "⚠️  Warning: EgyptianHistory-Ar-EB-part2.pdf not found in project root"
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

echo "   ✅ All prerequisites met"
echo ""

# ── Step 1: Stop existing containers ──────────────────────────
echo "🛑 [1/5] Stopping existing containers..."
docker compose down --remove-orphans 2>/dev/null || true
echo "   ✅ Containers stopped"
echo ""

# ── Step 2: Build all images ──────────────────────────────────
echo "🔨 [2/5] Building all Docker images (this may take a while)..."
docker compose build --no-cache
echo "   ✅ All images built successfully"
echo ""

# ── Step 3: Start services ───────────────────────────────────
echo "🚀 [3/5] Starting all services..."
docker compose up -d
echo "   ✅ Services started"
echo ""

# Wait for database to be ready
echo "   ⏳ Waiting for PostgreSQL to be ready..."
RETRIES=30
until docker compose exec -T postgres pg_isready -U teacher_ai -d teacher_ai_db > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
    RETRIES=$((RETRIES - 1))
    sleep 2
done

if [ $RETRIES -eq 0 ]; then
    echo "   ❌ PostgreSQL did not become ready in time"
    echo "   Check logs: docker compose logs postgres"
    exit 1
fi
echo "   ✅ PostgreSQL is ready"

# Wait for backend to be ready
echo "   ⏳ Waiting for backend to be ready..."
RETRIES=30
until docker compose exec -T backend curl -sf http://localhost:8000/api/health > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
    RETRIES=$((RETRIES - 1))
    sleep 3
done

if [ $RETRIES -eq 0 ]; then
    echo "   ⚠️  Backend did not respond to health check (may still be starting)"
    echo "   Continuing anyway..."
else
    echo "   ✅ Backend is ready"
fi
echo ""

# ── Step 4: Seed PDF references ──────────────────────────────
echo "📚 [4/5] Indexing PDF references into the knowledge base..."
echo "   (This processes the 2 Egyptian History PDF files)"
echo ""
docker compose exec -T backend python -m app.cli seed-pdfs
echo ""
echo "   ✅ PDF indexing complete"
echo ""

# ── Step 5: Set Telegram webhook ─────────────────────────────
echo "🤖 [5/5] Configuring Telegram webhook..."

# Read the domain from .env
DOMAIN=$(grep -E "^DOMAIN_NAME=" .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
if [ -n "$DOMAIN" ]; then
    docker compose exec -T backend python -m app.cli set-webhook "https://${DOMAIN}"
    echo "   ✅ Telegram webhook configured for https://${DOMAIN}"
else
    echo "   ⚠️  DOMAIN_NAME not set in .env — skipping webhook setup"
    echo "   You can set it later: docker compose exec backend python -m app.cli set-webhook https://your-domain.com"
fi
echo ""

# ── Final Status ─────────────────────────────────────────────
echo "============================================================"
echo "  🎉 Deployment Complete!"
echo "============================================================"
echo ""
echo "  📊 Services status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || docker compose ps
echo ""

# Show the URL
HTTP_PORT=$(grep -E "^HTTP_PORT=" .env | cut -d '=' -f2 | tr -d '"' || echo "8095")
HTTP_PORT=${HTTP_PORT:-8095}
echo "  🌐 Dashboard:   https://${DOMAIN:-localhost:${HTTP_PORT}}"
echo "  🔧 Backend API:  https://${DOMAIN:-localhost:${HTTP_PORT}}/api"
echo "  🤖 Telegram Bot: https://t.me/Gen_Assis_Bot"
echo ""
echo "  📋 Useful commands:"
echo "     docker compose logs -f backend    # Backend logs"
echo "     docker compose logs -f worker     # Worker logs (PDF processing)"
echo "     docker compose exec backend python -m app.cli bot-info"
echo ""
echo "============================================================"
