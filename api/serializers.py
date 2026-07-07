from rest_framework import serializers

from api.models import (
    NvidiaRecommendations,
    StartupBriefings,
    StartupClassifications,
    StartupSources,
    StartupValidations,
    Startups,
)


class StartupClassificationsSerializer(serializers.ModelSerializer):
    confidence = serializers.FloatField(read_only=True, allow_null=True)

    class Meta:
        model = StartupClassifications
        fields = ["id", "label", "confidence", "justification", "classified_at"]


class StartupValidationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupValidations
        fields = ["id", "is_valid", "issues", "source_count", "validated_at"]


class NvidiaRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NvidiaRecommendations
        fields = [
            "id", "nvidia_technology", "technical_justification",
            "business_justification", "priority", "implementation_complexity",
            "suggested_next_action", "created_at",
        ]


class StartupBriefingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupBriefings
        fields = ["id", "briefing_text", "created_at"]


class StartupSourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupSources
        fields = ["id", "url", "extraction_method", "fetched_at"]


class StartupListSerializer(serializers.ModelSerializer):
    ai_label = serializers.SerializerMethodField()
    ai_confidence = serializers.SerializerMethodField()
    source_count = serializers.SerializerMethodField()

    class Meta:
        model = Startups
        fields = [
            "id", "name", "sector", "funding_stage", "state",
            "ai_label", "ai_confidence", "source_count",
        ]

    def get_ai_label(self, obj) -> str | None:
        cls = obj.classifications.first()
        return cls.label if cls else None

    def get_ai_confidence(self, obj) -> float | None:
        cls = obj.classifications.first()
        return float(cls.confidence) if cls and cls.confidence else None

    def get_source_count(self, obj) -> int:
        return obj.sources.count()


class StartupDetailSerializer(serializers.ModelSerializer):
    classifications = StartupClassificationsSerializer(many=True, read_only=True)
    validations = StartupValidationsSerializer(many=True, read_only=True)
    recommendations = NvidiaRecommendationsSerializer(many=True, read_only=True)
    briefings = StartupBriefingsSerializer(many=True, read_only=True)
    sources = StartupSourcesSerializer(many=True, read_only=True)
    funding_amount_usd = serializers.FloatField(read_only=True, allow_null=True)

    class Meta:
        model = Startups
        fields = [
            "id", "name", "website", "sector", "description",
            "founders", "funding_stage", "funding_amount_usd",
            "employee_count_estimate", "ai_signals", "tech_stack_mentions",
            "state", "business_area", "program", "cohort_year",
            "inovativa_status", "created_at", "updated_at",
            "classifications", "validations", "recommendations",
            "briefings", "sources",
        ]
