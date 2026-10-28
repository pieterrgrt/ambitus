"""Write scripts/translations.py into the .po files and report what is missing.

Usage (from the project root):
    uv run python manage.py makemessages -l en -l de -l fr --ignore=.venv
    uv run python scripts/fill_translations.py
    uv run python manage.py compilemessages --ignore=.venv
"""

import sys
from pathlib import Path

import polib

sys.path.insert(0, str(Path(__file__).parent))
from translations import PLURALS, T  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "de", "fr"]

missing = set()
for i, lang in enumerate(LANGS):
    path = ROOT / "locale" / lang / "LC_MESSAGES" / "django.po"
    po = polib.pofile(str(path))
    po.metadata["Language"] = lang
    po.metadata["Content-Type"] = "text/plain; charset=UTF-8"
    po.metadata["Plural-Forms"] = "nplurals=2; plural=(n > 1);" if lang == "fr" else "nplurals=2; plural=(n != 1);"
    for entry in po:
        if entry.obsolete:
            continue
        if entry.msgid_plural:
            forms = PLURALS.get((entry.msgid, entry.msgid_plural))
            if forms:
                entry.msgstr_plural = {0: forms[i][0], 1: forms[i][1]}
            else:
                missing.add(entry.msgid)
        elif entry.msgid in T:
            entry.msgstr = T[entry.msgid][i]
        else:
            missing.add(entry.msgid)
        if "fuzzy" in entry.flags:
            entry.flags.remove("fuzzy")
    po.save()

if missing:
    print("Missing translations:")
    for msgid in sorted(missing):
        print(" -", msgid)
    sys.exit(1)
print("All strings translated.")
