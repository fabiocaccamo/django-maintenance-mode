from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, re_path

urlpatterns = [
    path("", lambda x: HttpResponse(), name="root"),
    re_path(r"^admin/", admin.site.urls),
]
