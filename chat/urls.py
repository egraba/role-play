from django.urls import path

import chat.views as cviews

urlpatterns = [
    path("<int:pk>/", cviews.RoomView.as_view(), name="room"),
]
