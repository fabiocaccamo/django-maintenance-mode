from django.urls import path

from maintenance_mode.views import maintenance_mode_off, maintenance_mode_on

urlpatterns = [
    path("off/", maintenance_mode_off, name="maintenance_mode_off"),
    path("on/", maintenance_mode_on, name="maintenance_mode_on"),
]
