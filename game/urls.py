from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("newgame", views.NewGameView.as_view(), name="newgame"),
    path("<int:game_id>/", views.GameView.as_view(), name="game"),
    path(
        "<int:game_id>/newnarrative",
        views.NewNarrativeView.as_view(),
        name="newnarrative",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/launch_dice/",
        views.DiceLaunchView.as_view(),
        name="launch_dice",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/make_choice/",
        views.ChoiceView.as_view(),
        name="make_choice",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/launch_dice/<int:action_id>/success/",
        views.DiceLaunchSuccessView.as_view(),
        name="dice_success",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/make_choice/<int:action_id>/success/",
        views.ChoiceSuccessView.as_view(),
        name="choice_success",
    ),
]
