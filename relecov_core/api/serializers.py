# Generic imports
from rest_framework import serializers

# Local imports
import relecov_core.models


class CreateBioinfoAnalysisValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.BioinfoAnalysisValue
        fields = "__all__"


class CreateDateAfterChangeStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.DateUpdateState
        fields = "__all__"


class CreateSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.Sample
        fields = "__all__"


class CreateEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.Effect
        fields = "__all__"


class CreateErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.Sample
        fields = "__all__"


class CreateVariantInSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.VariantInSample
        fields = "__all__"


class CreateVariantAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.VariantAnnotation
        fields = "__all__"


class CreateFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.Filter
        fields = "__all__"


class CreateVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.Variant
        fields = "__all__"


class CreateLineageValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.LineageValues
        fields = "__all__"


class CreatePublicDatabaseValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.PublicDatabaseValues
        fields = "__all__"


class UpdateStateSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = relecov_core.models.Sample
        fields = "__all__"
