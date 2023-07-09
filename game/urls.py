from django.urls import path

from game.views import common, master, player

urlpatterns = [
    path("", common.IndexView.as_view(), name="index"),
    path("games", common.ListGameView.as_view(), name="game-list"),
    path("<int:game_id>/", common.GameView.as_view(), name="game"),
    path(
        "create_game/<slug:story_slug>",
        common.CreateGameView.as_view(),
        name="game-create",
    ),
    path(
        "<int:game_id>/invite_character",
        master.InviteCharacterView.as_view(),
        name="game-invite-character",
    ),
    path(
        "<int:game_id>/invite_character/<int:pk>/confirm",
        master.InviteCharacterConfirmView.as_view(),
        name="game-invite-character-confirm",
    ),
    path(
        "<int:pk>/start_game",
        master.StartGameView.as_view(),
        name="game-start",
    ),
    path(
        "<int:pk>/start_game/error",
        master.StartGameErrorView.as_view(),
        name="game-start-error",
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
        name="pendingaction-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/increase_xp",
        master.IncreaseXpView.as_view(),
        name="xpincrease-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/damage",
        master.DamageView.as_view(),
        name="damage-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/heal",
        master.HealView.as_view(),
        name="healing-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/launch_dice/",
        player.DiceLaunchView.as_view(),
        name="dicelaunch-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/launch_dice/<int:action_id>/success/",
        player.DiceLaunchSuccessView.as_view(),
        name="dicelaunch-success",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/make_choice/",
        player.ChoiceView.as_view(),
        name="choice-create",
    ),
]
