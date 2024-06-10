# Generic imports
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Local imports
import relecov_dashboard.views


urlpatterns = [
    path("django_plotly_dash/", include("django_plotly_dash.urls")),
    # Methodology graphics
    path(
        "methodology",
        relecov_dashboard.views.methodology_index,
        name="methodology_index",
    ),
    path(
        "methodology/hostInfo",
        relecov_dashboard.views.methodology_host_info,
        name="methodology_host_info",
    ),
    path(
        "methodology/sequencing",
        relecov_dashboard.views.methodology_sequencing,
        name="methodology_sequencing",
    ),
    path(
        "methodology/sampleProcessing",
        relecov_dashboard.views.methodology_sample_processing,
        name="methodology_sample_processing",
    ),
    path(
        "methodology/bioinfo",
        relecov_dashboard.views.methodology_bioinfo,
        name="methodology_bioinfo",
    ),
    path("variants", relecov_dashboard.views.variants_index, name="variants_index"),
    path(
        "variants/mutationsInLineage",
        relecov_dashboard.views.mutations_in_lineage,
        name="mutations_in_lineage",
    ),
    path(
        "variants/spikeMutations3d",
        relecov_dashboard.views.spike_mutations_3d,
        name="spike_mutations_3d",
    ),
    path(
        "variants/lineagesVoc",
        relecov_dashboard.views.lineages_voc,
        name="lineages_voc",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
