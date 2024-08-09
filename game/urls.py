from django.urls import path

from .views import common, master

urlpatterns = [
    path("", common.IndexView.as_view(), name="index"),
    path("games", common.GameListView.as_view(), name="game-list"),
    path("<int:game_id>/", common.GameView.as_view(), name="game"),
    path(
        "create_game/<slug:campaign_slug>",
        common.GameCreateView.as_view(),
        name="game-create",
    ),
    path(
        "create_game/<slug:campaign_slug>/error",
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
        "<int:game_id>/request_ability_check",
        master.AbilityCheckRequestView.as_view(),
        name="ability-check-request-create",
    ),
    path(
        "<int:game_id>/create_combat",
        master.CombatCreateView.as_view(),
        name="combat-create",
    ),
]
