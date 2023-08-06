from django.urls import re_path

from game import consumers

websocket_urlpatterns = [
    re_path(r"ws/events/(?P<game_id>\w+)/$", consumers.EventsConsumer.as_asgi()),
]
