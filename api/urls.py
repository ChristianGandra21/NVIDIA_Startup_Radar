from django.urls import path

from api import views

urlpatterns = [
    path("startups/", views.startup_list, name="startup-list"),
    path("startups/search/", views.startup_search, name="startup-search"),
    path("startups/<int:pk>/", views.startup_detail, name="startup-detail"),
    path("startups/<int:pk>/analyze/", views.startup_analyze, name="startup-analyze"),
    path("stats/", views.startup_stats, name="startup-stats"),
]
