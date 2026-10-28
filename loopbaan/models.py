from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = settings.LANGUAGES


class Profile(models.Model):
    """What Ambitus knows about someone. Every AI action starts from this."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    situation = models.TextField(
        _("Waar sta je nu?"),
        blank=True,
        help_text=_("Bijvoorbeeld: net afgestudeerd, aan het werk maar wil iets anders, tussenjaar."),
    )
    education = models.TextField(_("Opleiding"), blank=True, help_text=_("Studies, diploma's, vakken die je goed lagen."))
    experience = models.TextField(
        _("Ervaring"), blank=True, help_text=_("Banen, stages, bijbanen, besturen, vrijwilligerswerk.")
    )
    skills = models.TextField(_("Waar ben je goed in?"), blank=True)
    interests = models.TextField(_("Wat interesseert je?"), blank=True)
    values = models.TextField(
        _("Wat vind je belangrijk in werk?"), blank=True, help_text=_("Bijvoorbeeld: zingeving, salaris, vrijheid, een team.")
    )
    languages = models.CharField(_("Talen die je spreekt"), max_length=255, blank=True)
    location = models.CharField(
        _("Waar wil je werken?"), max_length=255, blank=True, help_text=_("Steden, landen, of op afstand.")
    )
    constraints = models.TextField(
        _("Waar moet rekening mee gehouden worden?"),
        blank=True,
        help_text=_("Uren, startdatum, visum, wat je absoluut niet wilt."),
    )
    cv_text = models.TextField(
        _("Je cv"), blank=True, help_text=_("Plak hier de tekst van je huidige cv. Opmaak is niet nodig.")
    )
    updated_at = models.DateTimeField(auto_now=True)

    FIELDS_FOR_AI = [
        "situation",
        "education",
        "experience",
        "skills",
        "interests",
        "values",
        "languages",
        "location",
        "constraints",
    ]

    def __str__(self):
        return f"Profiel van {self.user}"

    @property
    def completeness(self):
        filled = sum(1 for name in self.FIELDS_FOR_AI + ["cv_text"] if getattr(self, name).strip())
        return round(100 * filled / (len(self.FIELDS_FOR_AI) + 1))


class Orientation(models.Model):
    """One run of the orientation questionnaire and the directions Claude suggested."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orientations")
    answers = models.JSONField(default=dict)
    summary = models.TextField(blank=True)
    directions = models.JSONField(default=list)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("orientation_detail", args=[self.pk])


class Application(models.Model):
    class Status(models.TextChoices):
        INTERESTED = "interesse", _("Interessant")
        PREPARING = "bezig", _("Mee bezig")
        APPLIED = "verstuurd", _("Verstuurd")
        INTERVIEW = "gesprek", _("Gesprek")
        OFFER = "aanbod", _("Aanbod")
        REJECTED = "afgewezen", _("Afgewezen")
        WITHDRAWN = "gestopt", _("Gestopt")

    ACTIVE = [Status.INTERESTED, Status.PREPARING, Status.APPLIED, Status.INTERVIEW, Status.OFFER]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    organisation = models.CharField(_("Organisatie"), max_length=200)
    role = models.CharField(_("Functie"), max_length=200)
    url = models.URLField(_("Link naar de vacature"), blank=True, max_length=500)
    location = models.CharField(_("Plaats"), max_length=200, blank=True)
    vacancy_text = models.TextField(
        _("Vacaturetekst"),
        blank=True,
        help_text=_("Plak de vacature hier. Ambitus gebruikt deze tekst voor je brief en je gesprek."),
    )
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.INTERESTED)
    deadline = models.DateField(_("Deadline"), null=True, blank=True)
    next_step = models.CharField(_("Volgende stap"), max_length=255, blank=True)
    next_step_date = models.DateField(_("Wanneer"), null=True, blank=True)
    contact = models.CharField(_("Contactpersoon"), max_length=255, blank=True)
    notes = models.TextField(_("Notities"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.role} – {self.organisation}"

    def get_absolute_url(self):
        return reverse("application_detail", args=[self.pk])

    @property
    def is_active(self):
        return self.status in self.ACTIVE

    @property
    def upcoming_date(self):
        """The nearest date that asks for action: the next step or the deadline."""
        dates = [d for d in (self.next_step_date, self.deadline) if d]
        return min(dates) if dates else None

    @property
    def is_overdue(self):
        date = self.upcoming_date
        return bool(date and date < timezone.localdate() and self.is_active)


class StatusChange(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20, choices=Application.Status.choices)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]


class Document(models.Model):
    """A motivation letter or CV advice written for one application."""

    class Kind(models.TextChoices):
        LETTER = "brief", _("Motivatiebrief")
        CV = "cv", _("Cv-advies")

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="documents")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    language = models.CharField(_("Taal"), max_length=5, choices=LANGUAGE_CHOICES)
    instructions = models.TextField(blank=True)
    content = models.TextField(_("Tekst"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("document_detail", args=[self.application_id, self.pk])


class InterviewPrep(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interview_preps")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    briefing = models.TextField(blank=True)
    questions = models.JSONField(default=list)
    questions_to_ask = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("interview_detail", args=[self.application_id, self.pk])


class PracticeAnswer(models.Model):
    prep = models.ForeignKey(InterviewPrep, on_delete=models.CASCADE, related_name="answers")
    question_index = models.PositiveSmallIntegerField()
    answer = models.TextField()
    feedback = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AIUsage(models.Model):
    """One call to the Claude API, for the monthly limit and cost overview."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_usage")
    action = models.CharField(max_length=40)
    model = models.CharField(max_length=60)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    ok = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
