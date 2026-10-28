from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("beheer/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("account/", include("accounts.urls")),
    path("", include("loopbaan.urls")),
]
