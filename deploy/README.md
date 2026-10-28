# Ambitus op een eigen server (naast andere sites)

Ambitus draait in Docker (Django + PostgreSQL) en luistert alleen op `127.0.0.1:8006`. De webserver die al op de server draait (Caddy of nginx) stuurt het domein door naar die poort en regelt HTTPS.

## Eenmalig

1. **DNS**: A-record voor het (sub)domein → IP van de server.
2. **Op de server:**
   ```bash
   git clone https://github.com/pieterrgrt/ambitus.git ~/ambitus
   cd ~/ambitus
   cp .env.example .env
   nano .env            # secret key, wachtwoord, domein, ANTHROPIC_API_KEY
   docker compose up -d --build
   curl http://127.0.0.1:8006/health   # moet "ok" geven
   ```
3. **Webserver**: voeg `deploy/Caddyfile.example` toe aan de bestaande config en herlaad.
4. **Eerste account (beheerder):**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
   Daarna uitnodigen via Account → Mensen uitnodigen, of:
   ```bash
   docker compose exec web python manage.py uitnodiging "Sanne"
   ```

## Alleen via Tailscale (zonder domein)

Zet in `.env`: `DJANGO_ALLOWED_HOSTS=100.65.113.117`, `DJANGO_CSRF_TRUSTED_ORIGINS=http://100.65.113.117:8006`, `DJANGO_SSL_REDIRECT=0`, en in `docker-compose.yml` de poort op `100.65.113.117:8006:8000`. Dan werkt het alleen voor apparaten in je tailnet; voor anderen is een domein nodig.

## Nieuwe versie live zetten

```bash
cd ~/ambitus && ./deploy/update.sh
```

## Back-up

```bash
docker compose exec db pg_dump -U ambitus ambitus > ambitus-$(date +%F).sql
```
