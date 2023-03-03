from django.urls import path

from game import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("create_game", views.NewGameView.as_view(), name="newgame"),
    path("<int:game_id>/", views.GameView.as_view(), name="game"),
    path(
        "<int:game_id>/add_character",
        views.AddCharacterView.as_view(),
        name="add_character",
    ),
    path(
        "<int:game_id>/add_character/<int:pk>/confirm",
        views.AddCharacterConfirmView.as_view(),
        name="add_character_confirm",
    ),
    path(
        "<int:game_id>/create_tale",
        views.CreateTaleView.as_view(),
        name="tale-create",
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
