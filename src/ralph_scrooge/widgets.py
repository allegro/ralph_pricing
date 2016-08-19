# -*- coding: utf-8 -*-
from django import forms
from django.utils.html import escape
from django.utils.safestring import mark_safe


class DateWidget(forms.DateInput):

    def render(self, name, value='', attrs=None, choices=()):
        if value is None:
            value = ''
        attr_class = escape(self.attrs.get('class', ''))
        attr_placeholder = escape(self.attrs.get('placeholder', ''))
        output = ('<input type="text" name="%s" class="datepicker %s" '
                  'placeholder="%s" value="%s" data-date-format="yyyy-mm-dd">')
        return mark_safe(output % (escape(name), attr_class,
                                   attr_placeholder, escape(value or '')))


class ReadOnlyDateWidget(forms.DateInput):

    def render(self, name, value, attrs=None, choices=()):
        formatted = escape(value) if value else ''
        return mark_safe('''
        <input type="hidden" name="%s" value="%s">
        <div>%s</div></input>''' % (
            escape(name), formatted, formatted))