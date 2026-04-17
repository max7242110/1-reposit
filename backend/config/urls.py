from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # v2 API (new architecture)
    path("api/v2/", include("catalog.urls")),
    path("api/v2/", include("core.urls")),
    path("api/v2/", include("reviews.urls")),
    path("api/v2/", include("submissions.urls")),
    # v1 legacy API (kept for backward compatibility)
    path("api/v1/", include(("ratings.urls", "ratings_v1"))),
    path("api/", include("ratings.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
