from django.http import HttpResponse
from django.urls import include, path

from .views import (
    ForceMaintenanceModeOffView,
    ForceMaintenanceModeOnView,
    force_maintenance_mode_off_view,
    force_maintenance_mode_on_view,
)

urlpatterns = [
    path(
        "",
        lambda x: HttpResponse(),
        name="root",
    ),
    path(
        "maintenance-mode-redirect/",
        lambda x: HttpResponse(),
        name="maintenance_mode_redirect",
    ),
    path(
        "maintenance-mode-off-view-func/",
        force_maintenance_mode_off_view,
        name="maintenance_mode_off_view_func",
    ),
    path(
        "maintenance-mode-off-view-class/",
        ForceMaintenanceModeOffView.as_view(),
        name="maintenance_mode_off_view_class",
    ),
    path(
        "maintenance-mode-on-view-func/",
        force_maintenance_mode_on_view,
        name="maintenance_mode_on_view_func",
    ),
    path(
        "maintenance-mode-on-view-class/",
        ForceMaintenanceModeOnView.as_view(),
        name="maintenance_mode_on_view_class",
    ),
    path(
        "maintenance-mode/",
        include("maintenance_mode.urls"),
    ),
]
