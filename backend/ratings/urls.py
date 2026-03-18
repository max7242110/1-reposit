from django.urls import path

from . import views

app_name = "ratings"

urlpatterns = [
    path("conditioners/", views.AirConditionerListView.as_view(), name="list"),
    path("conditioners/<int:pk>/", views.AirConditionerDetailView.as_view(), name="detail"),
]
