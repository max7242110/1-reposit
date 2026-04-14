from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path(
        "models/<int:model_id>/reviews/",
        views.ReviewListView.as_view(),
        name="review-list",
    ),
    path("reviews/", views.ReviewCreateView.as_view(), name="review-create"),
]
