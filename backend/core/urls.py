from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("pages/<slug:slug>/", views.PageDetailView.as_view(), name="page-detail"),
]
