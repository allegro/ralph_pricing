from django import template

register = template.Library()


@register.filter
def sort(values):
    return sorted(values)
