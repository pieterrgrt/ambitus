from django.conf import settings

SECTIONS = {
    "home": "home",
    "orientation": "orientation",
    "orientation_detail": "orientation",
    "profile": "profile",
}


def ambitus(request):
    match = getattr(request, "resolver_match", None)
    name = match.url_name if match else ""
    if name in SECTIONS:
        section = SECTIONS[name]
    elif match and match.route.startswith("sollicitaties/"):
        section = "applications"
    else:
        section = ""
    return {"LANGUAGE_CHOICES": settings.LANGUAGES, "section": section}
