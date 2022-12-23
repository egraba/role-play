from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:game_id>/', views.detail, name='detail'),
    path('<int:game_id>/<int:character_id>/launch_dice_request/', views.launch_dice_request, name='launch_dice_request'),
    path('<int:game_id>/<int:character_id>/launch_dice/', views.launch_dice, name='launch_dice'),
]