from django.urls import path

import master.views as mviews

urlpatterns = [
    path("story", mviews.DetailStoryView.as_view(), name="story-detail"),
]
