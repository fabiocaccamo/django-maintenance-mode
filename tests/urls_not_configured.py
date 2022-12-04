from django.http import HttpResponse
from django.urls import re_path

urlpatterns = [
    re_path(r"^$", lambda x: HttpResponse()),
]
