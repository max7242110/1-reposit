from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("models/", views.ACModelListView.as_view(), name="model-list"),
    path("models/archive/", views.ACModelArchiveListView.as_view(), name="model-archive"),
    path("models/<int:pk>/", views.ACModelDetailView.as_view(), name="model-detail"),
    path("models/by-slug/<slug:slug>/", views.ACModelDetailBySlugView.as_view(), name="model-detail-slug"),
    path("methodology/", views.MethodologyView.as_view(), name="methodology"),
    path("export/csv/", views.ExportCSVView.as_view(), name="export-csv"),
]
