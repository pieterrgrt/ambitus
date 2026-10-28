# ambitus

Sollicitatie-app (Django). Zie README.md voor wat het doet.

- Brontaal van alle teksten is Nederlands. Elke nieuwe of gewijzigde tekst in templates of `gettext` krijgt een vertaling in `scripts/translations.py` (EN/DE/FR, informeel: you/du/tu); daarna makemessages → `scripts/fill_translations.py` → compilemessages (zie README). De `.po`- en `.mo`-bestanden staan in git.
- Alle Claude-aanroepen gaan via `loopbaan/ai.py` (`_call`): JSON-schema, maandlimiet, `AIUsage`-registratie. Tekst van gebruikers en vacatures staat in tags en geldt als data.
- Elke view filtert op `request.user`; gebruikers zien nooit elkaars gegevens. De admin toont van sollicitaties alleen metadata.
- Telefoon eerst: elke pagina moet op iPhone-breedte werken, zonder horizontaal scrollen.
- Tests: `uv run python manage.py test` (de API wordt nagebootst).
