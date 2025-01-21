# Local imports
import core.models
import core.api.serializers
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status


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

def add_sample_state_history(sample_obj, state_id, error_name=None):
    """
    Adds a new state history entry for a sample and marks previous states as not current.
    Since all 
    """
    # Validate the state exists
    state_obj = None
    if state_id:
        state_obj = core.models.SampleState.objects.filter(pk=state_id).last()

    # Validate the state exists or fetch the last state for the sample
    if state_id:
        state_obj = core.models.SampleState.objects.filter(pk=state_id).last()
    else:
        # If no state is defined, use the last record for that sample 
        state_obj = (
            core.models.SampleStateHistory.objects.filter(sample=sample_obj)
            .order_by('-changed_at')
            .first()
        )

    # Si no se encuentra ningún estado, levantar una excepción
    if not state_obj:
        raise ValueError("No valid state found for the sample.")

    # Handle error_name if provided
    if error_name:
        error_name_obj = core.models.ErrorName.objects.filter(
            error_name=error_name
        ).last()
    else:
        # Assign the 'other' entry with pk=1 as default
        error_name_obj = core.models.ErrorName.objects.filter(pk=999).first()

    # Mark previous states as not current
    core.models.SampleStateHistory.objects.filter(
        sample=sample_obj, is_current=True
    ).update(is_current=False)

    # Add the new state history
    state_history_obj = {
        "is_current": True,
        "changed_at": timezone.now(),
        "sample": sample_obj.pk,
        "state": state_obj.pk,
        "error_name": error_name_obj.pk,
    }

    # Serialization
    state_history_serializer = core.api.serializers.SampleStateHistorySerializer(
        data=state_history_obj
    )
    # Validation
    if not state_history_serializer.is_valid():
        return Response(
            state_history_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    state_history_serializer.save()
    return True
