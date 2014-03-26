# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect

from ralph_pricing.app import Scrooge
from ralph_pricing.forms import TeamDaterangeFormSet
from ralph_pricing.menus import teams_menu
from ralph_pricing.models import Team
from ralph_pricing.views.base import Base


class Teams(Base):
    template_name = 'ralph_pricing/teams.html'

    def __init__(self, *args, **kwargs):
        super(Teams, self).__init__(*args, **kwargs)
        self.formset = None
        self.team = None
        self.team_name = None

    def init_args(self):
        self.team_name = self.kwargs.get('team')
        if self.team_name is not None:
            self.team = get_object_or_404(
                Team,
                name=self.team_name,
            )

    def post(self, *args, **kwargs):
        self.init_args()
        if self.team:
            self.formset = TeamDaterangeFormSet(
                self.request.POST,
                queryset=self.team.dateranges.order_by('start'),
            )
            for form in self.formset.extra_forms:
                if form.has_changed():
                    form.instance.team = self.team
            if self.formset.is_valid():
                self.formset.save()
                messages.success(self.request, "Teams dateranges updated.")
                return HttpResponseRedirect(self.request.path)
            else:
                messages.error(self.request, "Please fix the errors.")
        return super(Teams, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.init_args()
        if self.team_name:
            self.formset = TeamDaterangeFormSet(
                queryset=self.team.dateranges.order_by('start'),
            )
        return super(Teams, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Teams, self).get_context_data(**kwargs)
        context.update({
            'section': 'teams',
            'sidebar_items': teams_menu(
                '/{0}/teams'.format(Scrooge.url_prefix),
                self.team_name
            ),
            'sidebar_selected': self.team_name,
            'formset': self.formset,
        })
        return context
