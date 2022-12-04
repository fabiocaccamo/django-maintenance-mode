from django.contrib import admin
from django.http import HttpResponse
from django.urls import re_path

urlpatterns = [
    re_path(r"^$", lambda x: HttpResponse(), name="root"),
    re_path(r"^admin/", admin.site.urls),
]
