from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("models/", views.ACModelListView.as_view(), name="model-list"),
    path("models/<int:pk>/", views.ACModelDetailView.as_view(), name="model-detail"),
    path("methodology/", views.MethodologyView.as_view(), name="methodology"),
    path("export/csv/", views.ExportCSVView.as_view(), name="export-csv"),
]
