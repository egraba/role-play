from django.urls import path

from .views import (
    CampaignCreateView,
    CampaignDetailView,
    CampaignListView,
    CampaignUpdateView,
)

urlpatterns = [
    path(
        "campaign/<slug:slug>/",
        CampaignDetailView.as_view(),
        name="campaign-detail",
    ),
    path("campaigns/", CampaignListView.as_view(), name="campaign-list"),
    path("campaign", CampaignCreateView.as_view(), name="campaign-create"),
    path(
        "campaign/<slug:slug>/update",
        CampaignUpdateView.as_view(),
        name="campaign-update",
    ),
]
