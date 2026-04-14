from __future__ import annotations

from rest_framework.generics import RetrieveAPIView

from .models import Page
from .serializers import PageSerializer


class PageDetailView(RetrieveAPIView):
    serializer_class = PageSerializer
    lookup_field = "slug"
    queryset = Page.objects.filter(is_active=True)
