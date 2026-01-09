"""
URL configuration for the core project.

Defines the main URL routes for admin access,
authentication, video APIs, and Django RQ dashboard.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("auth_app.api.urls")),
    path("api/", include("video_app.api.urls")),
    path("django-rq/", include("django_rq.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

