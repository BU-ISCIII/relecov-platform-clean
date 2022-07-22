from django.urls import path
from django.conf import settings
from relecov_documentation import views
from django.conf.urls.static import static

from django.urls import include

urlpatterns = [
    path("", views.documentation, name="documentation"),
    path(
        "createUserAccount/",
        views.documentation_create_user_account,
        name="create_user_account",
    ),
    path("Intranet/", views.documentation_intranet, name="intranet"),
    path("Dashboard/", views.documentation_dashboard, name="dashboard"),
    path("markdownx/", include("markdownx.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
