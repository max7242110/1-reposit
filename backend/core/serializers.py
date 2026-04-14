from __future__ import annotations

from rest_framework import serializers

from .models import Page


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["slug", "title_ru", "content_ru"]
        read_only_fields = fields
