from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # v2 API (new architecture)
    path("api/v2/", include("catalog.urls")),
    # v1 legacy API (kept for backward compatibility)
    path("api/v1/", include(("ratings.urls", "ratings_v1"))),
    path("api/", include("ratings.urls")),
]
