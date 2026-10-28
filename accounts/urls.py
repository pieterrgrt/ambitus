from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EmailLoginForm

urlpatterns = [
    path(
        "inloggen/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html", authentication_form=EmailLoginForm, redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("uitloggen/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "wachtwoord/",
        auth_views.PasswordChangeView.as_view(template_name="accounts/password.html", success_url="/account/"),
        name="password_change",
    ),
    path("aanmelden/<str:token>/", views.signup, name="signup"),
    path("", views.account, name="account"),
    path("export/", views.export, name="account_export"),
    path("verwijderen/", views.delete, name="account_delete"),
    path("uitnodigingen/", views.invites, name="invites"),
]
