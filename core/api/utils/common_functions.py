# Local imports
import core.models
import core.api.serializers


def get_schema_version_if_exists(data):
    """Check if schema name and schema version exists"""
    apps_name = __package__.split(".")[0]
    print("apps_name", apps_name)
    print(data)
    if "schema_name" in data and "schema_version" in data:
        if core.models.Schema.objects.filter(
            schema_name__iexact=data["schema_name"],
            schema_version__iexact=data["schema_version"],
            schema_apps_name__iexact=apps_name,
        ).exists():
            return core.models.Schema.objects.filter(
                schema_name__iexact=data["schema_name"],
                schema_version__iexact=data["schema_version"],
                schema_apps_name__iexact=apps_name,
            ).last()
    return None


def get_analysis_defined(s_obj):
    return core.models.BioinfoAnalysisValue.objects.filter(
        bioinfo_analysis_fieldID__property_name="analysis_date", sample=s_obj
    ).values_list("value", flat=True)


def update_change_state_date(sample_id, state_id):
    """Update the DateUpdateState table with the new sample state"""
    d_date = {"stateID": state_id, "sampleID": sample_id}
    date_update_serializer = (
        core.api.serializers.CreateDateAfterChangeStateSerializer(data=d_date)
    )
    if date_update_serializer.is_valid():
        date_update_serializer.save()
    return
