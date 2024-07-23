# Generic imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local imports
import relecov_documentation

urlpatterns = [
    path("", relecov_documentation.views.index, name="index"),
    path("description", relecov_documentation.views.description, name="description"),
    path("relecovInstall/", relecov_documentation.views.relecov_install, name="relecov_install"),
    path("configuration/", relecov_documentation.views.configuration, name="configuration"),
    path("metadata/", relecov_documentation.views.metadata, name="metadata"),
    path("metadataLabExcel/", relecov_documentation.views.metadata_lab_excel, name="metadata_lab_excel"),
    path("relecovTools/", relecov_documentation.views.relecov_tools, name="relecov_tools"),
    path("intranetOverview/", relecov_documentation.views.intranet_overview, name="intranet_overview"),
    path(
        "intranetContactData/",
        relecov_documentation.views.intranet_contact_data,
        name="intranet_contact_data",
    ),
    path(
        "intranetSampleSearch/",
        relecov_documentation.views.intranet_sample_search,
        name="intranet_sample_search",
    ),
    path(
        "intranetReceivedSamples/",
        relecov_documentation.views.intranet_received_samples,
        name="intranet_received_samples",
    ),
    path(
        "intranetUploadMetadata/",
        relecov_documentation.views.intranet_upload_metadata,
        name="intranet_upload_metadata",
    ),
    path("variantDashboard/", relecov_documentation.views.variant_dashboard, name="variant_dashboard"),
    path(
        "methodologyDashboard/",
        relecov_documentation.views.methodology_dashboard,
        name="methodology_dashboard",
    ),
    path("nextstrainInstall/", relecov_documentation.views.nextstrain_install, name="nextstrain_install"),
    path("howtoNextstrain/", relecov_documentation.views.howto_nextstrain, name="howto_nextstrain"),
    path("uploadToEna/", relecov_documentation.views.upload_to_ena, name="upload_to_ena"),
    path("uploadToGisaid/", relecov_documentation.views.upload_to_gisaid, name="upload_to_gisaid"),
    path("apiSchema/", relecov_documentation.views.api_schema, name="api_schema"),
    path("howtoApi/", relecov_documentation.views.howto_api, name="howto_api"),
    path(
        "createNewUser/",
        relecov_documentation.views.create_new_user,
        name="create_new_user",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
