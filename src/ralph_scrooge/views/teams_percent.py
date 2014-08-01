# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect

from ralph_scrooge.app import Scrooge
from ralph_scrooge.forms import TeamServicePercentFormSet
from ralph_scrooge.menus import teams_menu
from ralph_scrooge.models import Team, TeamDaterange, TeamServicePercent
from ralph_scrooge.views.base import Base


class TeamsPercent(Base):
    template_name = 'ralph_scrooge/teams_percent.html'

    def __init__(self, *args, **kwargs):
        super(TeamsPercent, self).__init__(*args, **kwargs)
        self.formset = None
        self.team = None
        self.team_name = None
        self.daterange = None
        self.ventures_percent = None

    def init_args(self):
        self.team_name = self.kwargs.get('team')
        if self.kwargs.get('daterange'):
            self.daterange = get_object_or_404(
                TeamDaterange,
                id=self.kwargs['daterange']
            )
        if self.team_name is not None:
            self.team = get_object_or_404(
                Team,
                name=self.team_name,
            )
            if self.daterange is not None:
                self.ventures_percent = TeamServicePercent.objects.filter(
                    team_daterange=self.daterange
                )

    def post(self, *args, **kwargs):
        self.init_args()
        if self.daterange:
            self.formset = TeamServicePercentFormSet(
                self.request.POST,
                queryset=TeamServicePercent.objects.filter(
                    team_daterange=self.daterange
                ).order_by('venture'),
            )
            for form in self.formset.extra_forms:
                if form.has_changed():
                    form.instance.team_daterange = self.daterange
            if self.formset.is_valid():
                self.formset.save()
                messages.success(
                    self.request,
                    "Team ventures percent updated."
                )
                return HttpResponseRedirect(self.request.path)
            else:
                messages.error(self.request, "Please fix the errors.")
        return super(TeamsPercent, self).get(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.init_args()
        if self.daterange:
            self.formset = TeamServicePercentFormSet(
                queryset=TeamServicePercent.objects.filter(
                    team_daterange=self.daterange
                ).order_by('venture'),
            )
        return super(TeamsPercent, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TeamsPercent, self).get_context_data(**kwargs)

        context.update({
            'section': 'teams',
            'sidebar_items': teams_menu(
                '/{0}/teams'.format(Scrooge.url_prefix),
                self.team_name,
            ),
            'sidebar_selected': self.daterange.id,
            'formset': self.formset,
        })
        return context
