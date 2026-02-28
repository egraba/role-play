from django.urls import path

from . import views

app_name = "adventure"

urlpatterns = [
    path("", views.CampaignListView.as_view(), name="campaign-list"),
    path("new/", views.CampaignCreateView.as_view(), name="campaign-create"),
    path("<slug:slug>/", views.CampaignDetailView.as_view(), name="campaign-detail"),
    path(
        "<slug:slug>/edit/", views.CampaignUpdateView.as_view(), name="campaign-update"
    ),
    path(
        "<slug:slug>/delete/",
        views.CampaignDeleteView.as_view(),
        name="campaign-delete",
    ),
]
