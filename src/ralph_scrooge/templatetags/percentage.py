from django import template
from django.http import QueryDict

register = template.Library()


@register.filter
def percentage(value, args):
    """Usage (var = 0.99123):
    var|percentage:""                ->     99%
    var|percentage:"dec=2"           ->  99.12%
    var|percentage:"dec=2&sign=true" -> +99.12%
    """
    qs = QueryDict(args)
    dec_places = int(qs.get('dec', 0))
    sign = qs.get('sign')
    if sign and sign.lower() == 'true':
        format_str = '{:+.' + str(dec_places) + '%}'
    else:
        format_str = '{:.' + str(dec_places) + '%}'
    return format_str.format(value)
