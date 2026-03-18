from rest_framework import serializers

from .models import AirConditioner, ParameterValue


class ParameterValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterValue
        fields = ["id", "parameter_name", "raw_value", "unit", "score"]


class AirConditionerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirConditioner
        fields = ["id", "rank", "brand", "model_name", "total_score"]


class AirConditionerDetailSerializer(serializers.ModelSerializer):
    parameters = ParameterValueSerializer(many=True, read_only=True)

    class Meta:
        model = AirConditioner
        fields = [
            "id",
            "rank",
            "brand",
            "model_name",
            "youtube_url",
            "rutube_url",
            "vk_url",
            "total_score",
            "parameters",
        ]
