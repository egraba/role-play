from django.urls import path

import master.views as mviews

urlpatterns = [
    path("story/<slug:slug>/", mviews.DetailStoryView.as_view(), name="story-detail"),
    path("stories/", mviews.ListStoryView.as_view(), name="story-list"),
    path("story", mviews.CreateStoryView.as_view(), name="story-create"),
    path(
        "story/<slug:slug>/update",
        mviews.UpdateStoryView.as_view(),
        name="story-update",
    ),
]
