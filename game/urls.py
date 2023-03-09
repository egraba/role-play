from django.urls import path

from game.views import common, master, player

urlpatterns = [
    path("", common.IndexView.as_view(), name="index"),
    path("<int:game_id>/", common.GameView.as_view(), name="game"),
    path(
        "character/<int:pk>",
        common.DetailCharacterView.as_view(),
        name="character-detail",
    ),
    path("create_game", master.CreateGameView.as_view(), name="game-create"),
    path(
        "<int:game_id>/add_character",
        master.AddCharacterView.as_view(),
        name="game-add-character",
    ),
    path(
        "<int:game_id>/add_character/<int:pk>/confirm",
        master.AddCharacterConfirmView.as_view(),
        name="game-add-character-confirm",
    ),
    path(
        "<int:pk>/start_game",
        master.StartGameView.as_view(),
        name="game-start",
    ),
    path(
        "<int:pk>/end_game",
        master.EndGameView.as_view(),
        name="game-end",
    ),
    path(
        "<int:game_id>/create_tale",
        master.CreateTaleView.as_view(),
        name="tale-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/add_pending_action",
        master.CreatePendingActionView.as_view(),
        name="character-add-pending-action",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/increase_xp",
        master.IncreaseXpView.as_view(),
        name="character-increase-xp",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/damage",
        master.DamageView.as_view(),
        name="character-damage",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/heal",
        master.HealView.as_view(),
        name="character-heal",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/launch_dice/",
        player.DiceLaunchView.as_view(),
        name="launch_dice",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/make_choice/",
        player.ChoiceView.as_view(),
        name="make_choice",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/launch_dice/<int:action_id>/success/",
        player.DiceLaunchSuccessView.as_view(),
        name="dice_success",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/make_choice/<int:action_id>/success/",
        player.ChoiceSuccessView.as_view(),
        name="choice_success",
    ),
]
