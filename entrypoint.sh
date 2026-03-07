#!/bin/sh
set -e

echo "============================================"
echo "  Comper Closet — Production Startup"
echo "============================================"

# ─── Wait for PostgreSQL ──────────────────────────────────────────────────────
echo "[1/4] Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
MAX_RETRIES=30
RETRY=0
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -q; do
  RETRY=$((RETRY + 1))
  if [ "$RETRY" -ge "$MAX_RETRIES" ]; then
    echo "ERROR: PostgreSQL did not become ready after $MAX_RETRIES attempts. Exiting."
    exit 1
  fi
  echo "  Attempt $RETRY/$MAX_RETRIES — retrying in 2s..."
  sleep 2
done
echo "  ✔ PostgreSQL is ready."

# ─── Run Migrations ──────────────────────────────────────────────────────────
echo "[2/4] Running database migrations..."
python manage.py migrate --noinput
echo "  ✔ Migrations complete."

# ─── Collect Static Files ─────────────────────────────────────────────────────
echo "[3/4] Collecting static files..."
python manage.py collectstatic --noinput
echo "  ✔ Static files collected."

# ─── Start Gunicorn ──────────────────────────────────────────────────────────
echo "[4/4] Starting Gunicorn..."
echo "============================================"

exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --worker-class sync \
    --worker-connections 1000 \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level "${GUNICORN_LOG_LEVEL:-info}" \
    --access-logfile - \
    --error-logfile -
