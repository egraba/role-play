from django.core.cache import cache
from django.views.generic import DetailView

import chat.models as cmodels


class RoomView(DetailView):
    model = cmodels.Room
    template_name = "chat/room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object
        messages = cache.get(f"room{room.id}_messages")
        if not messages:
            messages = cmodels.Message.objects.filter(room=room.id).order_by("date")[
                :20
            ]
            cache.set(f"room{room.id}_messages", messages)
        context["message_list"] = messages

        return context
