from django.views.generic import DetailView

import chat.models as cmodels


class RoomView(DetailView):
    model = cmodels.Room
    template_name = "chat/room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object
        context["message_list"] = cmodels.Message.objects.filter(room=room.id).order_by(
            "date"
        )
        return context
