from django.urls import path

from game.views import common, master

urlpatterns = [
    path("", common.IndexView.as_view(), name="index"),
    path("games", common.GameListView.as_view(), name="game-list"),
    path("<int:game_id>/", common.GameView.as_view(), name="game"),
    path(
        "create_game/<slug:story_slug>",
        common.GameCreateView.as_view(),
        name="game-create",
    ),
    path(
        "create_game/<slug:story_slug>/error",
        common.GameCreateErrorView.as_view(),
        name="game-create-error",
    ),
    path(
        "<int:game_id>/invite_character",
        master.CharacterInviteView.as_view(),
        name="game-invite-character",
    ),
    path(
        "<int:game_id>/invite_character/<int:pk>/confirm",
        master.CharacterInviteConfirmView.as_view(),
        name="game-invite-character-confirm",
    ),
    path(
        "<int:pk>/start_game",
        master.GameStartView.as_view(),
        name="game-start",
    ),
    path(
        "<int:pk>/start_game/error",
        master.GameStartErrorView.as_view(),
        name="game-start-error",
    ),
    path(
        "<int:game_id>/create_quest",
        master.QuestCreateView.as_view(),
        name="quest-create",
    ),
    path(
        "<int:game_id>/create_instruction",
        master.InstructionCreateView.as_view(),
        name="instruction-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/increase_xp",
        master.XpIncreaseView.as_view(),
        name="xpincrease-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/damage",
        master.DamageView.as_view(),
        name="damage-create",
    ),
    path(
        "<int:game_id>/character/<int:character_id>/heal",
        master.HealingView.as_view(),
        name="healing-create",
    ),
]
