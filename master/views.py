from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView

import master.forms as mforms
import master.models as mmodels


class StoryDetailView(LoginRequiredMixin, DetailView):
    model = mmodels.Story
    template_name = "master/story.html"


class StoryListView(LoginRequiredMixin, ListView):
    model = mmodels.Story
    paginate_by = 20
    ordering = ["title"]
    template_name = "master/story_list.html"


class StoryCreateView(LoginRequiredMixin, CreateView):
    form_class = mforms.StoryCreateForm
    template_name = "master/story_create.html"


class StoryUpdateView(LoginRequiredMixin, UpdateView):
    model = mmodels.Story
    form_class = mforms.StoryUpdateForm
    template_name = "master/story_update.html"
