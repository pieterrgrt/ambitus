import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone, translation
from django.utils.translation import gettext as _

from loopbaan.export import user_data

from .forms import AccountForm, InviteForm, SignupForm
from .models import Invite, User


def signup(request, token):
    invite = get_object_or_404(Invite, token=token)
    if not invite.is_usable:
        return render(request, "accounts/invite_invalid.html", status=410)
    if request.user.is_authenticated:
        return redirect("home")

    form = SignupForm(request.POST or None, initial={"language": translation.get_language()})
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            invite = Invite.objects.select_for_update().get(pk=invite.pk)
            if not invite.is_usable:
                return render(request, "accounts/invite_invalid.html", status=410)
            user = User.objects.create_user(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                language=form.cleaned_data["language"],
            )
            invite.used_by = user
            invite.used_at = timezone.now()
            invite.save(update_fields=["used_by", "used_at"])
        login(request, user)
        translation.activate(user.language)
        messages.success(request, _("Welkom bij Ambitus! Begin met je profiel, dan kan Ambitus je beter helpen."))
        return redirect("profile")
    return render(request, "accounts/signup.html", {"form": form, "invite": invite})


@login_required
def account(request):
    form = AccountForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        translation.activate(request.user.language)
        messages.success(request, _("Opgeslagen."))
        return redirect("account")
    return render(request, "accounts/account.html", {"form": form})


@login_required
def export(request):
    data = json.dumps(user_data(request.user), ensure_ascii=False, indent=2, default=str)
    response = HttpResponse(data, content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="ambitus-export.json"'
    return response


@login_required
def delete(request):
    if request.method == "POST" and request.POST.get("confirm") == request.user.email:
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, _("Je account en al je gegevens zijn verwijderd."))
        return redirect("home")
    if request.method == "POST":
        messages.error(request, _("Typ je e-mailadres precies over om te bevestigen."))
    return render(request, "accounts/delete.html")


@staff_member_required(login_url="login")
def invites(request):
    form = InviteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        invite = form.save(commit=False)
        invite.created_by = request.user
        invite.save()
        messages.success(request, _("Uitnodiging gemaakt. Kopieer de link en stuur hem door."))
        return redirect("invites")
    return render(
        request,
        "accounts/invites.html",
        {"form": form, "invites": Invite.objects.select_related("used_by")[:50]},
    )
