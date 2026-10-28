from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import Application, Document, Profile
from .orientation import QUESTIONS


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ["user", "updated_at"]
        widgets = {
            name: forms.Textarea(attrs={"rows": 3})
            for name in ["situation", "education", "experience", "skills", "interests", "values", "constraints"]
        } | {"cv_text": forms.Textarea(attrs={"rows": 12})}


class OrientationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, question in QUESTIONS:
            self.fields[key] = forms.CharField(
                label=question, required=False, widget=forms.Textarea(attrs={"rows": 3})
            )

    def answer_pairs(self):
        return [(str(question), self.cleaned_data.get(key, "")) for key, question in QUESTIONS]

    def clean(self):
        cleaned = super().clean()
        if sum(1 for key, _q in QUESTIONS if cleaned.get(key, "").strip()) < 3:
            raise forms.ValidationError(_("Beantwoord minstens drie vragen, dan heeft Ambitus genoeg om mee te werken."))
        return cleaned


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        super().__init__(format="%Y-%m-%d", **kwargs)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            "organisation",
            "role",
            "status",
            "url",
            "location",
            "deadline",
            "next_step",
            "next_step_date",
            "contact",
            "vacancy_text",
            "notes",
        ]
        widgets = {
            "deadline": DateInput(),
            "next_step_date": DateInput(),
            "vacancy_text": forms.Textarea(attrs={"rows": 8}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class StatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]


class LanguageField(forms.ChoiceField):
    def __init__(self, **kwargs):
        super().__init__(label=_("Taal"), choices=settings.LANGUAGES, **kwargs)


class LetterRequestForm(forms.Form):
    language = LanguageField()
    instructions = forms.CharField(
        label=_("Wensen (optioneel)"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text=_("Bijvoorbeeld: noem mijn stage bij de gemeente, houd het formeel, korter."),
    )


class LanguageRequestForm(forms.Form):
    language = LanguageField()


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["content"]
        widgets = {"content": forms.Textarea(attrs={"rows": 20})}


class PracticeForm(forms.Form):
    question_index = forms.IntegerField(widget=forms.HiddenInput, min_value=0)
    answer = forms.CharField(label=_("Jouw antwoord"), widget=forms.Textarea(attrs={"rows": 6}))
