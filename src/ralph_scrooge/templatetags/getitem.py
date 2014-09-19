from django import template

register = template.Library()


@register.filter
def getitem(item, key):
    return item.get(key, '')
