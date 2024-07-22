# Generic imports
from django.urls import path

# Local imports
import relecov_core.api

app_name = "relecov_api"


urlpatterns = [
    path(
        "createBioinfoData",
        relecov_core.api.views.create_bioinfo_metadata,
        name="create_bioinfo_data",
    ),
    path(
        "createSampleData",
        relecov_core.api.views.create_sample_data,
        name="create_sample_data",
    ),
    path(
        "createVariantData",
        relecov_core.api.views.create_variant_data,
        name="create_variant_data",
    ),
    path("updateState", relecov_core.api.views.update_state, name="update_state"),
]
