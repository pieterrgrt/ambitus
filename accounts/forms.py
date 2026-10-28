from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import Invite, User


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("E-mailadres"), widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"})
    )


class SignupForm(forms.Form):
    first_name = forms.CharField(label=_("Voornaam"), max_length=150)
    email = forms.EmailField(label=_("E-mailadres"), widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    password = forms.CharField(
        label=_("Wachtwoord"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=_("Minstens 10 tekens."),
    )
    language = forms.ChoiceField(label=_("Taal"), choices=User._meta.get_field("language").choices)
    privacy = forms.BooleanField(label=_("Ik heb gelezen hoe Ambitus met mijn gegevens omgaat."))

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Er bestaat al een account met dit e-mailadres."))
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        if password:
            candidate = User(email=cleaned.get("email", ""), first_name=cleaned.get("first_name", ""))
            try:
                password_validation.validate_password(password, candidate)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return cleaned


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "language"]
        labels = {"first_name": _("Voornaam"), "language": _("Taal")}


class InviteForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ["note"]
        widgets = {"note": forms.TextInput(attrs={"placeholder": _("Bijvoorbeeld: Sanne, studiegenoot")})}
