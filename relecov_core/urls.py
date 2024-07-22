# Generic imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local imports
import relecov_core.views

urlpatterns = [
    path("", relecov_core.views.index, name="index"),
    path(
        "annotationDisplay=<int:annot_id>",
        relecov_core.views.annotation_display,
        name="annotation_display",
    ),
    path(
        "assignSamplesToUser",
        relecov_core.views.assign_samples_to_user,
        name="assign_samples_to_user",
    ),
    path("Contact", relecov_core.views.contact, name="contact"),
    path("intranet/", relecov_core.views.intranet, name="intranet"),
    path(
        "laboratoryContact/",
        relecov_core.views.laboratory_contact,
        name="laboratory_contact",
    ),
    path("metadataForm", relecov_core.views.metadata_form, name="metadataForm"),
    path(
        "metadataVisualization/",
        relecov_core.views.metadata_visualization,
        name="metadataVisualization",
    ),
    path(
        "organismAnnotation",
        relecov_core.views.organism_annotation,
        name="organism_annotation",
    ),
    path(
        "sampleDisplay=<int:sample_id>",
        relecov_core.views.sample_display,
        name="sample_display",
    ),
    path(
        "receivedSamples", relecov_core.views.received_samples, name="received_samples"
    ),
    path(
        "schemaDisplay=<int:schema_id>",
        relecov_core.views.schema_display,
        name="schema_display",
    ),
    path("schemaHandling", relecov_core.views.schema_handling, name="schema_handling"),
    path("searchSample", relecov_core.views.search_sample, name="search_sample"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
