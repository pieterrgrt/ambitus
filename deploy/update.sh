#!/bin/sh
# Pull the latest version and restart. Run from the repository root.
set -e
cd "$(dirname "$0")/.."
git pull --ff-only
docker compose up -d --build
for i in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${AMBITUS_PORT:-8006}/health" >/dev/null; then
    echo "Ambitus draait."
    exit 0
  fi
  sleep 2
done
echo "Ambitus antwoordt niet op /health. Kijk in: docker compose logs web" >&2
exit 1
