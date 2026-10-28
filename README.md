# Ambitus

Een sollicitatie-app voor mensen die net klaar zijn met studeren en niet goed weten wat ze nu willen. Werkt op uitnodiging, in het Nederlands, Engels, Duits en Frans, en is gemaakt voor de telefoon (ook als app op het beginscherm te zetten).

## Wat het doet

- **Profiel**: opleiding, ervaring, wat je belangrijk vindt, waar je wilt werken, je cv. Alle AI-hulp bouwt hierop.
- **Oriëntatie**: acht open vragen, daarna stelt Claude 3 tot 5 richtingen voor, met concrete functies, waar je zoekt en wat je deze week kunt proberen. Een functie tik je aan om hem als sollicitatie bij te houden.
- **Sollicitaties**: per vacature de status (interessant → mee bezig → verstuurd → gesprek → aanbod / afgewezen / gestopt), deadline, volgende stap en notities. Het overzicht toont wat binnenkort speelt.
- **Brief en cv**: een motivatiebrief in de gekozen taal, volgens de gewoonten van dat land (Anschreiben, lettre de motivation), en concreet advies om je cv op de vacature af te stemmen. Alles is daarna te bewerken en te kopiëren.
- **Gesprek voorbereiden**: waarschijnlijke vragen met uitleg, je eigen oefenantwoorden met feedback, en vragen die je zelf kunt stellen.
- **Account**: taal kiezen, al je gegevens downloaden (JSON), account met alles verwijderen.
- **Beheer**: staff-accounts maken uitnodigingslinks onder Account → Mensen uitnodigen (of `python manage.py uitnodiging "naam"`). In `/beheer/` staat het AI-gebruik per persoon met tokens.

## Techniek

Django 6 met server-rendered templates, PostgreSQL in productie (SQLite lokaal), Claude via de Anthropic SDK (`loopbaan/ai.py`). Het model staat in `AMBITUS_MODEL` (standaard `claude-opus-5-5`). Elke AI-actie vraagt JSON volgens een schema, telt mee voor de maandlimiet (`AMBITUS_AI_MONTHLY_LIMIT`, staff onbeperkt) en gebruikt de server-side fallback van de API (`fallbacks: "default"`) als een verzoek wordt geweigerd.

## Lokaal

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py compilemessages --ignore=.venv
uv run python manage.py createsuperuser
ANTHROPIC_API_KEY=... uv run python manage.py runserver
```

Tests (de Claude API wordt nagebootst, kost niets): `uv run python manage.py test`

## Vertalingen

Brontaal is Nederlands. De vertalingen naar Engels, Duits en Frans staan in `scripts/translations.py`. Na tekstwijzigingen:

```bash
uv run python manage.py makemessages -l en -l de -l fr --ignore=.venv
uv run python scripts/fill_translations.py   # meldt welke teksten nog een vertaling missen
uv run python manage.py compilemessages --ignore=.venv
```

## Op de server

Zie `deploy/README.md`.
