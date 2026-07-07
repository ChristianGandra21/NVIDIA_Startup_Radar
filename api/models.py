from django.db import models


class Startups(models.Model):
    name = models.TextField()
    website = models.TextField(blank=True, null=True)
    sector = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    founders = models.TextField(blank=True, null=True)
    funding_stage = models.TextField(blank=True, null=True)
    funding_amount_usd = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    employee_count_estimate = models.TextField(blank=True, null=True)
    ai_signals = models.TextField(blank=True, null=True)
    tech_stack_mentions = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    business_area = models.TextField(blank=True, null=True)
    program = models.TextField(blank=True, null=True)
    cohort_year = models.IntegerField(blank=True, null=True)
    cohort_cycle = models.TextField(blank=True, null=True)
    inovativa_status = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "startups"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class StartupClassifications(models.Model):
    startup = models.ForeignKey(Startups, on_delete=models.DO_NOTHING, related_name="classifications")
    label = models.TextField()
    confidence = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    justification = models.TextField(blank=True, null=True)
    classified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "startup_classifications"
        ordering = ["-classified_at"]

    def __str__(self) -> str:
        return f"{self.startup.name}: {self.label}"


class StartupValidations(models.Model):
    startup = models.ForeignKey(Startups, on_delete=models.DO_NOTHING, related_name="validations")
    is_valid = models.BooleanField()
    issues = models.TextField(blank=True, null=True)
    source_count = models.IntegerField(blank=True, null=True)
    validated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "startup_validations"
        ordering = ["-validated_at"]


class NvidiaRecommendations(models.Model):
    startup = models.ForeignKey(Startups, on_delete=models.DO_NOTHING, related_name="recommendations")
    nvidia_technology = models.TextField()
    technical_justification = models.TextField(blank=True, null=True)
    business_justification = models.TextField(blank=True, null=True)
    priority = models.TextField(blank=True, null=True)
    implementation_complexity = models.TextField(blank=True, null=True)
    suggested_next_action = models.TextField(blank=True, null=True)
    evidence = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "nvidia_recommendations"
        ordering = ["-priority", "nvidia_technology"]

    def __str__(self) -> str:
        return f"{self.startup.name} -> {self.nvidia_technology}"


class StartupBriefings(models.Model):
    startup = models.ForeignKey(Startups, on_delete=models.DO_NOTHING, related_name="briefings")
    briefing_text = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "startup_briefings"
        ordering = ["-created_at"]


class StartupSources(models.Model):
    startup = models.ForeignKey(Startups, on_delete=models.DO_NOTHING, related_name="sources")
    url = models.TextField()
    extraction_method = models.TextField()
    raw_excerpt = models.TextField(blank=True, null=True)
    fetched_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "startup_sources"
        unique_together = (("startup", "url"),)
