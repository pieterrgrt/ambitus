from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone, translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from . import ai
from .forms import (
    ApplicationForm,
    DocumentForm,
    LanguageRequestForm,
    LetterRequestForm,
    OrientationForm,
    PracticeForm,
    ProfileForm,
    StatusForm,
)
from .models import Application, Document, InterviewPrep, Profile, StatusChange


def _profile(user):
    profile, _created = Profile.objects.get_or_create(user=user)
    return profile


def _ai_error_message(error):
    if isinstance(error, ai.AILimitReached):
        return _("Je hebt deze maand je AI-acties opgebruikt. Volgende maand kun je weer verder.")
    return {
        "refused": _("Hier kon Ambitus geen antwoord op geven. Pas je tekst aan en probeer het opnieuw."),
        "busy": _("Het is even druk. Probeer het over een minuut opnieuw."),
        "unreachable": _("Ambitus kon de AI niet bereiken. Probeer het later opnieuw."),
        "config": _("De AI is nog niet goed ingesteld. Laat het de beheerder weten."),
    }.get(error.args[0] if error.args else "", _("Er ging iets mis. Probeer het opnieuw."))


def _default_language(request):
    return request.user.language or translation.get_language()


def _my_application(request, pk):
    return get_object_or_404(Application, pk=pk, user=request.user)


def home(request):
    if not request.user.is_authenticated:
        return render(request, "loopbaan/landing.html")

    profile = _profile(request.user)
    applications = request.user.applications.all()
    active = [a for a in applications if a.is_active]
    upcoming = sorted((a for a in active if a.upcoming_date), key=lambda a: a.upcoming_date)[:5]
    counts = {
        row["status"]: row["n"] for row in applications.order_by().values("status").annotate(n=Count("id"))
    }
    status_counts = [(label, counts.get(value, 0)) for value, label in Application.Status.choices if value in Application.ACTIVE]
    return render(
        request,
        "loopbaan/home.html",
        {
            "profile": profile,
            "orientation": request.user.orientations.first(),
            "upcoming": upcoming,
            "status_counts": status_counts,
            "active_count": len(active),
            "remaining": ai.remaining_this_month(request.user),
            "today": timezone.localdate(),
        },
    )


def privacy(request):
    return render(request, "loopbaan/privacy.html")


@login_required
def profile(request):
    instance = _profile(request.user)
    form = ProfileForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Je profiel is opgeslagen."))
        next_url = request.POST.get("next", "")
        if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("home")
    return render(request, "loopbaan/profile.html", {"form": form, "profile": instance})


@login_required
def orientation(request):
    form = OrientationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        language = _default_language(request)
        answers = form.answer_pairs()
        try:
            result = ai.suggest_directions(request.user, _profile(request.user), answers, language)
        except ai.AIError as error:
            messages.error(request, _ai_error_message(error))
        else:
            item = request.user.orientations.create(
                answers=[{"question": q, "answer": a} for q, a in answers],
                summary=result["summary"],
                directions=result["directions"],
                language=language,
            )
            return redirect(item)
    return render(
        request,
        "loopbaan/orientation.html",
        {
            "form": form,
            "history": request.user.orientations.all()[:10],
            "profile": _profile(request.user),
            "remaining": ai.remaining_this_month(request.user),
        },
    )


@login_required
def orientation_detail(request, pk):
    item = get_object_or_404(request.user.orientations, pk=pk)
    return render(request, "loopbaan/orientation_detail.html", {"item": item})


@login_required
@require_POST
def orientation_delete(request, pk):
    get_object_or_404(request.user.orientations, pk=pk).delete()
    messages.success(request, _("Verwijderd."))
    return redirect("orientation")


@login_required
def applications(request):
    show = request.GET.get("toon", "actief")
    items = request.user.applications.all()
    if show == "afgerond":
        items = items.exclude(status__in=Application.ACTIVE)
    else:
        items = items.filter(status__in=Application.ACTIVE)
    groups = []
    for value, label in Application.Status.choices:
        group = [a for a in items if a.status == value]
        if group:
            groups.append((value, label, group))
    return render(request, "loopbaan/applications.html", {"groups": groups, "show": show})


@login_required
def application_new(request):
    initial = {"role": request.GET.get("functie", "")}
    form = ApplicationForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.save()
        StatusChange.objects.create(application=item, status=item.status)
        messages.success(request, _("Toegevoegd."))
        return redirect(item)
    return render(request, "loopbaan/application_form.html", {"form": form})


@login_required
def application_detail(request, pk):
    item = _my_application(request, pk)
    return render(
        request,
        "loopbaan/application_detail.html",
        {
            "item": item,
            "status_form": StatusForm(instance=item),
            "documents": item.documents.all(),
            "preps": item.interview_preps.all(),
            "history": item.history.all(),
            "remaining": ai.remaining_this_month(request.user),
        },
    )


@login_required
def application_edit(request, pk):
    item = _my_application(request, pk)
    old_status = item.status
    form = ApplicationForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        item = form.save()
        if item.status != old_status:
            StatusChange.objects.create(application=item, status=item.status)
        messages.success(request, _("Opgeslagen."))
        return redirect(item)
    return render(request, "loopbaan/application_form.html", {"form": form, "item": item})


@login_required
@require_POST
def application_status(request, pk):
    item = _my_application(request, pk)
    old_status = item.status
    form = StatusForm(request.POST, instance=item)
    if form.is_valid():
        item = form.save()
        if item.status != old_status:
            StatusChange.objects.create(application=item, status=item.status)
    return redirect(item)


@login_required
def application_delete(request, pk):
    item = _my_application(request, pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Verwijderd."))
        return redirect("applications")
    return render(request, "loopbaan/confirm_delete.html", {"object": item, "back": item.get_absolute_url()})


@login_required
def letter_new(request, pk):
    item = _my_application(request, pk)
    form = LetterRequestForm(request.POST or None, initial={"language": _default_language(request)})
    if request.method == "POST" and form.is_valid():
        language = form.cleaned_data["language"]
        instructions = form.cleaned_data["instructions"]
        try:
            result = ai.write_letter(request.user, _profile(request.user), item, language, instructions)
        except ai.AIError as error:
            messages.error(request, _ai_error_message(error))
        else:
            notes = "\n".join(f"- {n}" for n in result["notes_for_you"])
            document = item.documents.create(
                kind=Document.Kind.LETTER, language=language, instructions=notes, content=result["letter"]
            )
            if item.status == Application.Status.INTERESTED:
                item.status = Application.Status.PREPARING
                item.save(update_fields=["status", "updated_at"])
                StatusChange.objects.create(application=item, status=item.status)
            return redirect(document)
    return render(
        request,
        "loopbaan/ai_request.html",
        {
            "item": item,
            "form": form,
            "title": _("Motivatiebrief schrijven"),
            "intro": _("Ambitus schrijft een eerste versie op basis van je profiel, je cv en de vacaturetekst. Daarna pas je hem zelf aan."),
            "needs_vacancy": not item.vacancy_text.strip(),
            "remaining": ai.remaining_this_month(request.user),
        },
    )


@login_required
def cv_new(request, pk):
    item = _my_application(request, pk)
    form = LanguageRequestForm(request.POST or None, initial={"language": _default_language(request)})
    if request.method == "POST" and form.is_valid():
        language = form.cleaned_data["language"]
        try:
            result = ai.cv_advice(request.user, _profile(request.user), item, language)
        except ai.AIError as error:
            messages.error(request, _ai_error_message(error))
        else:
            document = item.documents.create(kind=Document.Kind.CV, language=language, content=_cv_text(result))
            return redirect(document)
    return render(
        request,
        "loopbaan/ai_request.html",
        {
            "item": item,
            "form": form,
            "title": _("Cv afstemmen"),
            "intro": _("Ambitus vergelijkt je cv met de vacature en zegt wat je kunt aanpassen."),
            "needs_vacancy": not item.vacancy_text.strip(),
            "needs_cv": not _profile(request.user).cv_text.strip(),
            "remaining": ai.remaining_this_month(request.user),
        },
    )


def _cv_text(result):
    parts = [result["verdict"], ""]
    for number, change in enumerate(result["changes"], 1):
        parts.append(f"{number}. {change['section']}: {change['suggestion']}")
        if change["example"].strip():
            parts.append(f"   → {change['example']}")
        parts.append("")
    if result["keywords"]:
        parts.append(_("Woorden uit de vacature:") + " " + ", ".join(result["keywords"]))
    return "\n".join(parts).strip()


@login_required
def document_detail(request, pk, doc_pk):
    item = _my_application(request, pk)
    document = get_object_or_404(item.documents, pk=doc_pk)
    form = DocumentForm(request.POST or None, instance=document)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Opgeslagen."))
        return redirect(document)
    return render(request, "loopbaan/document_detail.html", {"item": item, "document": document, "form": form})


@login_required
def document_delete(request, pk, doc_pk):
    item = _my_application(request, pk)
    document = get_object_or_404(item.documents, pk=doc_pk)
    if request.method == "POST":
        document.delete()
        messages.success(request, _("Verwijderd."))
        return redirect(item)
    return render(request, "loopbaan/confirm_delete.html", {"object": document.get_kind_display(), "back": document.get_absolute_url()})


@login_required
def interview_new(request, pk):
    item = _my_application(request, pk)
    form = LanguageRequestForm(request.POST or None, initial={"language": _default_language(request)})
    if request.method == "POST" and form.is_valid():
        language = form.cleaned_data["language"]
        try:
            result = ai.interview_prep(request.user, _profile(request.user), item, language)
        except ai.AIError as error:
            messages.error(request, _ai_error_message(error))
        else:
            prep = item.interview_preps.create(
                language=language,
                briefing=result["briefing"],
                questions=result["questions"],
                questions_to_ask=result["questions_to_ask"],
            )
            return redirect(prep)
    return render(
        request,
        "loopbaan/ai_request.html",
        {
            "item": item,
            "form": form,
            "title": _("Gesprek voorbereiden"),
            "intro": _("Ambitus bedenkt de vragen die je waarschijnlijk krijgt, met uitleg hoe je ze aanpakt. Daarna kun je antwoorden oefenen en feedback krijgen."),
            "needs_vacancy": not item.vacancy_text.strip(),
            "remaining": ai.remaining_this_month(request.user),
        },
    )


@login_required
def interview_detail(request, pk, prep_pk):
    item = _my_application(request, pk)
    prep = get_object_or_404(item.interview_preps, pk=prep_pk)
    practice_by_question = {}
    for answer in prep.answers.all():
        practice_by_question.setdefault(answer.question_index, []).append(answer)
    questions = [
        {"index": i, **q, "practice": practice_by_question.get(i, [])} for i, q in enumerate(prep.questions)
    ]
    return render(
        request,
        "loopbaan/interview_detail.html",
        {
            "item": item,
            "prep": prep,
            "questions": questions,
            "open_index": request.GET.get("vraag"),
            "remaining": ai.remaining_this_month(request.user),
        },
    )


@login_required
@require_POST
def interview_practice(request, pk, prep_pk):
    item = _my_application(request, pk)
    prep = get_object_or_404(item.interview_preps, pk=prep_pk)
    form = PracticeForm(request.POST)
    if not form.is_valid() or form.cleaned_data["question_index"] >= len(prep.questions):
        messages.error(request, _("Schrijf eerst een antwoord."))
        return redirect(prep)
    index = form.cleaned_data["question_index"]
    answer = form.cleaned_data["answer"]
    try:
        feedback = ai.answer_feedback(
            request.user, _profile(request.user), item, prep.questions[index]["question"], answer, prep.language
        )
    except ai.AIError as error:
        messages.error(request, _ai_error_message(error))
    else:
        prep.answers.create(question_index=index, answer=answer, feedback=feedback)
    return redirect(f"{prep.get_absolute_url()}?vraag={index}#vraag-{index}")


@login_required
def interview_delete(request, pk, prep_pk):
    item = _my_application(request, pk)
    prep = get_object_or_404(item.interview_preps, pk=prep_pk)
    if request.method == "POST":
        prep.delete()
        messages.success(request, _("Verwijderd."))
        return redirect(item)
    return render(request, "loopbaan/confirm_delete.html", {"object": _("Gespreksvoorbereiding"), "back": prep.get_absolute_url()})
