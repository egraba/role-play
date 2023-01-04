from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:game_id>/', views.GameView.as_view(), name='game'),
    path('<int:game_id>/character/<int:character_id>/launch_dice/', views.DiceLaunchView.as_view(), name='launch_dice'),
    path('<int:game_id>/character/<int:character_id>/action/<int:action_id>/success/', views.SuccessView.as_view(), name='success'),
]