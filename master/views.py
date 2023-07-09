from django.views.generic import CreateView, DetailView, ListView, UpdateView

import master.forms as mforms
import master.models as mmodels


class DetailStoryView(DetailView):
    model = mmodels.Story
    template_name = "master/story.html"


class ListStoryView(ListView):
    model = mmodels.Story
    paginate_by = 20
    template_name = "master/storylist.html"


class CreateStoryView(CreateView):
    form_class = mforms.CreateStoryForm
    template_name = "master/createstory.html"


class UpdateStoryView(UpdateView):
    model = mmodels.Story
    fields = ["synopsis", "main_conflict", "objective"]
    template_name = "master/updatestory.html"
