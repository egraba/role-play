from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponseBase
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CampaignForm
from .models import Campaign


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = "adventure/campaign_list.html"
    context_object_name = "campaigns"

    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter(owner=self.request.user)


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = "adventure/campaign_detail.html"
    context_object_name = "campaign"

    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter(owner=self.request.user)


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "adventure/campaign_form.html"

    def form_valid(self, form: CampaignForm) -> HttpResponseBase:
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "adventure/campaign_form.html"

    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter(owner=self.request.user)


class CampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = Campaign
    template_name = "adventure/campaign_confirm_delete.html"
    success_url = reverse_lazy("adventure:campaign-list")

    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter(owner=self.request.user)
