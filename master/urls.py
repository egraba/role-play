from django.urls import path

import master.views as mviews

urlpatterns = [
    path("story/<slug:slug>/", mviews.StoryDetailView.as_view(), name="story-detail"),
    path("stories/", mviews.StoryListView.as_view(), name="story-list"),
    path("story", mviews.StoryCreateView.as_view(), name="story-create"),
    path(
        "story/<slug:slug>/update",
        mviews.StoryUpdateView.as_view(),
        name="story-update",
    ),
]
