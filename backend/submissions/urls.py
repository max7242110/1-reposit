from django.urls import path

from .views import ACSubmissionCreateView, BrandListView

urlpatterns = [
    path("brands/", BrandListView.as_view(), name="brand-list"),
    path("submissions/", ACSubmissionCreateView.as_view(), name="submission-create"),
]
