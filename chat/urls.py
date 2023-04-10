from django.urls import path

import chat.views as cviews

urlpatterns = [
    path("<str:room_name>/", cviews.room, name="room"),
]
