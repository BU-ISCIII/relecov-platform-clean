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


def handle_sample_errors(dict_error):
    """
    Validate error type. If the error is not defined in the database,
    assign the 'Other' error type.
    """
    # Search for the error by name
    error_name_obj = core.models.ErrorName.objects.filter(
        error_name=dict_error.get("error_name")
    ).last()

    # If not found by name, search using the error code (optional)
    if not error_name_obj and dict_error.get("error_code"):
        error_name_obj = core.models.ErrorName.objects.filter(
            error_code=dict_error["error_code"]
        ).last()

    # If the error is still not found, assign "Other" as the default error
    if not error_name_obj:
        error_name_obj = core.models.ErrorName.objects.filter(
            error_code="999"  # Code for "Other"
        ).last()

    # Return the identified or assigned ErrorName object
    return error_name_obj

# TODO: Would it be possilbe to return a serializer object instead?
def add_sample_state_history(sample_obj, state_id, error_name=None):
    """
    Adds a new state history entry for a sample and marks previous states as not current.
    """
    # Validate the state exists
    state_obj = core.models.SampleState.objects.filter(pk=state_id).last()
    if not state_obj:
        raise ValueError(f"State '{state_id}' does not exist.")

    # Handle error_name if provided
    error_obj = None
    if error_name:
        error_obj = handle_sample_errors({"error_name": error_name})
    else:
        # Assign the 'No Error' entry with pk=1 as default
        error_obj = core.models.ErrorName.objects.filter(pk=1).first()
        if not error_obj:
            raise ValueError("Default error entry with pk=1 does not exist in the database.")

    # Mark previous states as not current
    core.models.SampleStateHistory.objects.filter(
        sample=sample_obj,
        is_current=True
    ).update(is_current=False)

    # Add the new state history
    state_data = {
        "is_current": True,
        "changed_at": timezone.now(),
        "sample": sample_obj.pk,
        "state": state_obj.pk,
        "error_name": error_obj.pk
    }
    # TODO: needs is_valid assestment. 
    state_serializer = core.api.serializers.SampleStateHistorySerializer(
        data=state_data
    )
    if not state_serializer.is_valid():
        Response(status=status.HTTP_201_CREATED)
    state_serializer.save()
    return state_obj