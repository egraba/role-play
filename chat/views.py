from django.views.generic import DetailView

import chat.models as cmodels


class RoomView(DetailView):
    model = cmodels.Room
    template_name = "chat/room.html"
