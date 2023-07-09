from django.urls import path

import master.views as mviews

urlpatterns = [
    path("story/<slug:slug>", mviews.DetailStoryView.as_view(), name="story-detail"),
    path("story", mviews.CreateStoryView.as_view(), name="story-create"),
]
