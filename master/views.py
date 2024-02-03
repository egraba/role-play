from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CampaignCreateForm, CampaignUpdateForm
from .models import Campaign


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = "master/campaign.html"


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    paginate_by = 20
    ordering = ["title"]
    template_name = "master/campaign_list.html"


class CampaignCreateView(LoginRequiredMixin, CreateView):
    form_class = CampaignCreateForm
    template_name = "master/campaign_create.html"


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignUpdateForm
    template_name = "master/campaign_update.html"
