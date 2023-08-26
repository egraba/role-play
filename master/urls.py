from django.urls import path

import master.views as mviews

urlpatterns = [
    path(
        "campaign/<slug:slug>/",
        mviews.CampaignDetailView.as_view(),
        name="campaign-detail",
    ),
    path("campaigns/", mviews.CampaignListView.as_view(), name="campaign-list"),
    path("campaign", mviews.CampaignCreateView.as_view(), name="campaign-create"),
    path(
        "campaign/<slug:slug>/update",
        mviews.CampaignUpdateView.as_view(),
        name="campaign-update",
    ),
]
