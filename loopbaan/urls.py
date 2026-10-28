from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("privacy/", views.privacy, name="privacy"),
    path("profiel/", views.profile, name="profile"),
    path("orientatie/", views.orientation, name="orientation"),
    path("orientatie/<int:pk>/", views.orientation_detail, name="orientation_detail"),
    path("orientatie/<int:pk>/verwijderen/", views.orientation_delete, name="orientation_delete"),
    path("sollicitaties/", views.applications, name="applications"),
    path("sollicitaties/nieuw/", views.application_new, name="application_new"),
    path("sollicitaties/<int:pk>/", views.application_detail, name="application_detail"),
    path("sollicitaties/<int:pk>/bewerken/", views.application_edit, name="application_edit"),
    path("sollicitaties/<int:pk>/status/", views.application_status, name="application_status"),
    path("sollicitaties/<int:pk>/verwijderen/", views.application_delete, name="application_delete"),
    path("sollicitaties/<int:pk>/brief/", views.letter_new, name="letter_new"),
    path("sollicitaties/<int:pk>/cv/", views.cv_new, name="cv_new"),
    path("sollicitaties/<int:pk>/documenten/<int:doc_pk>/", views.document_detail, name="document_detail"),
    path(
        "sollicitaties/<int:pk>/documenten/<int:doc_pk>/verwijderen/",
        views.document_delete,
        name="document_delete",
    ),
    path("sollicitaties/<int:pk>/gesprek/", views.interview_new, name="interview_new"),
    path("sollicitaties/<int:pk>/gesprek/<int:prep_pk>/", views.interview_detail, name="interview_detail"),
    path("sollicitaties/<int:pk>/gesprek/<int:prep_pk>/oefenen/", views.interview_practice, name="interview_practice"),
    path(
        "sollicitaties/<int:pk>/gesprek/<int:prep_pk>/verwijderen/",
        views.interview_delete,
        name="interview_delete",
    ),
]
