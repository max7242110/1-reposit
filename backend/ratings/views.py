from rest_framework import generics

from .models import AirConditioner
from .serializers import AirConditionerDetailSerializer, AirConditionerListSerializer


class AirConditionerListView(generics.ListAPIView):
    queryset = AirConditioner.objects.all().order_by("-total_score")
    serializer_class = AirConditionerListSerializer


class AirConditionerDetailView(generics.RetrieveAPIView):
    queryset = AirConditioner.objects.prefetch_related("parameters").all()
    serializer_class = AirConditionerDetailSerializer
