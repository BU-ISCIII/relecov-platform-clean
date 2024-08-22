# Generic imports
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Local imports
import docs.views

urlpatterns = [
    path("", docs.views.index, name="index"),
    path("description", docs.views.description, name="description"),
    path(
        "relecovInstall/",
        docs.views.relecov_install,
        name="relecov_install",
    ),
    path(
        "configuration/",
        docs.views.configuration,
        name="configuration",
    ),
    path("metadata/", docs.views.metadata, name="metadata"),
    path(
        "metadataLabExcel/",
        docs.views.metadata_lab_excel,
        name="metadata_lab_excel",
    ),
    path(
        "relecovTools/", docs.views.relecov_tools, name="relecov_tools"
    ),
    path(
        "intranetOverview/",
        docs.views.intranet_overview,
        name="intranet_overview",
    ),
    path(
        "intranetContactData/",
        docs.views.intranet_contact_data,
        name="intranet_contact_data",
    ),
    path(
        "intranetSampleSearch/",
        docs.views.intranet_sample_search,
        name="intranet_sample_search",
    ),
    path(
        "intranetReceivedSamples/",
        docs.views.intranet_received_samples,
        name="intranet_received_samples",
    ),
    path(
        "intranetUploadMetadata/",
        docs.views.intranet_upload_metadata,
        name="intranet_upload_metadata",
    ),
    path(
        "variantDashboard/",
        docs.views.variant_dashboard,
        name="variant_dashboard",
    ),
    path(
        "methodologyDashboard/",
        docs.views.methodology_dashboard,
        name="methodology_dashboard",
    ),
    path(
        "nextstrainInstall/",
        docs.views.nextstrain_install,
        name="nextstrain_install",
    ),
    path(
        "howtoNextstrain/",
        docs.views.howto_nextstrain,
        name="howto_nextstrain",
    ),
    path(
        "uploadToEna/", docs.views.upload_to_ena, name="upload_to_ena"
    ),
    path(
        "uploadToGisaid/",
        docs.views.upload_to_gisaid,
        name="upload_to_gisaid",
    ),
    path("apiSchema/", docs.views.api_schema, name="api_schema"),
    path("howtoApi/", docs.views.howto_api, name="howto_api"),
    path(
        "createNewUser/",
        docs.views.create_new_user,
        name="create_new_user",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
