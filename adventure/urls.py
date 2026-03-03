from django.urls import path

from . import views

app_name = "adventure"

urlpatterns = [
    # Campaign
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
    # Acts (nested under campaign slug)
    path(
        "<slug:slug>/acts/new/",
        views.ActCreateView.as_view(),
        name="act-create",
    ),
    path(
        "<slug:slug>/acts/<int:pk>/",
        views.ActDetailView.as_view(),
        name="act-detail",
    ),
    path(
        "<slug:slug>/acts/<int:pk>/edit/",
        views.ActUpdateView.as_view(),
        name="act-update",
    ),
    path(
        "<slug:slug>/acts/<int:pk>/delete/",
        views.ActDeleteView.as_view(),
        name="act-delete",
    ),
    # Scenes (nested under act_pk, which is under campaign slug)
    path(
        "<slug:slug>/acts/<int:act_pk>/scenes/new/",
        views.SceneCreateView.as_view(),
        name="scene-create",
    ),
    path(
        "<slug:slug>/acts/<int:act_pk>/scenes/<int:pk>/",
        views.SceneDetailView.as_view(),
        name="scene-detail",
    ),
    path(
        "<slug:slug>/acts/<int:act_pk>/scenes/<int:pk>/edit/",
        views.SceneUpdateView.as_view(),
        name="scene-update",
    ),
    path(
        "<slug:slug>/acts/<int:act_pk>/scenes/<int:pk>/delete/",
        views.SceneDeleteView.as_view(),
        name="scene-delete",
    ),
    # NPCs (flat under campaign)
    path(
        "<slug:slug>/npcs/new/",
        views.NPCCreateView.as_view(),
        name="npc-create",
    ),
    path(
        "<slug:slug>/npcs/<int:pk>/edit/",
        views.NPCUpdateView.as_view(),
        name="npc-update",
    ),
    path(
        "<slug:slug>/npcs/<int:pk>/delete/",
        views.NPCDeleteView.as_view(),
        name="npc-delete",
    ),
    # Locations (flat under campaign)
    path(
        "<slug:slug>/locations/new/",
        views.LocationCreateView.as_view(),
        name="location-create",
    ),
    path(
        "<slug:slug>/locations/<int:pk>/edit/",
        views.LocationUpdateView.as_view(),
        name="location-update",
    ),
    path(
        "<slug:slug>/locations/<int:pk>/delete/",
        views.LocationDeleteView.as_view(),
        name="location-delete",
    ),
    # Encounters (nested under scene)
    path(
        "<slug:slug>/acts/<int:act_pk>/scenes/<int:scene_pk>/encounters/new/",
        views.EncounterCreateView.as_view(),
        name="encounter-create",
    ),
    path(
        "<slug:slug>/acts/<int:act_pk>/scenes/<int:scene_pk>/encounters/<int:pk>/edit/",
        views.EncounterUpdateView.as_view(),
        name="encounter-update",
    ),
    path(
        "<slug:slug>/acts/<int:act_pk>/scenes/<int:scene_pk>/encounters/<int:pk>/delete/",
        views.EncounterDeleteView.as_view(),
        name="encounter-delete",
    ),
]
