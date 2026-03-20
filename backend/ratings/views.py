from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import generics

from .models import AirConditioner
from .serializers import AirConditionerDetailSerializer, AirConditionerListSerializer


class AirConditionerListView(generics.ListAPIView):
    serializer_class = AirConditionerListSerializer

    def get_queryset(self) -> QuerySet[AirConditioner]:
        return AirConditioner.objects.order_by("-total_score")


class AirConditionerDetailView(generics.RetrieveAPIView):
    serializer_class = AirConditionerDetailSerializer

    def get_queryset(self) -> QuerySet[AirConditioner]:
        return AirConditioner.objects.prefetch_related("parameters")
