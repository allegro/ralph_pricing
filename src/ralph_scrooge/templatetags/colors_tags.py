from django import template

from ralph_scrooge.models import PricingObjectColor

register = template.Library()


@register.inclusion_tag('templatetags/panels_colors.html')
def panels_colors():
    return {
        'colors': [
            {
                'value': choice.desc,
                'category': choice.name,
            }
            for choice in PricingObjectColor.__choices__
        ]
    }
