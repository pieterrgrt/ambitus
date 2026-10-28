from django.utils.translation import gettext_lazy as _

# The orientation questionnaire. Short, open questions: the answers are read
# by Claude together with the profile, so free text works better than scales.
QUESTIONS = [
    ("energy", _("Wanneer had je de afgelopen jaren het gevoel dat de tijd vloog? Wat deed je toen?")),
    ("drain", _("Van welk soort taken of omgevingen word je moe of chagrijnig?")),
    ("proud", _("Waar ben je trots op, binnen of buiten je studie?")),
    ("people", _("Werk je liever alleen, in een klein team of met veel mensen? Met wie het liefst?")),
    ("impact", _("Op welk gebied zou je iets willen veranderen of bijdragen?")),
    ("day", _("Beschrijf een werkdag over drie jaar waar je blij van zou worden.")),
    ("fear", _("Wat houdt je tegen, of waar ben je onzeker over?")),
    ("dealbreakers", _("Wat wil je in je eerste baan absoluut niet?")),
]
