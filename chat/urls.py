from django.urls import path

import chat.views as cviews

urlpatterns = [
    path("", cviews.index, name="index"),
]
