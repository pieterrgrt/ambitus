FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /usr/local/bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends gettext && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_DEBUG=0

WORKDIR /app

# Install dependencies first so this layer is cached between code changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput && \
    DJANGO_SECRET_KEY=build-only python manage.py compilemessages --ignore=.venv

# AI requests can take a minute, so workers get a long timeout; threads keep
# other visitors served while one request waits for Claude.
CMD python manage.py migrate --noinput && \
    gunicorn config.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 300 --access-logfile -
