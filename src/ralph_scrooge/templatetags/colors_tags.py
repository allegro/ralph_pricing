from django import template

from ralph_scrooge.models import PricingObjectType

register = template.Library()


@register.inclusion_tag('templatetags/panels_colors.html')
def panels_colors():

    return {
        'colors': [
            {
                'value': choice.color,
                'category': choice.name,
            }
            for choice in PricingObjectType.objects.all()
        ]
    }
