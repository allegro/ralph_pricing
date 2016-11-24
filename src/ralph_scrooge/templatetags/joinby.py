from django import template

register = template.Library()


@register.filter
def joinby(values, sep):
    """Usage (values = [1, 2, 3]):
    values|joinby:", " -> "1, 2, 3"
    (and yes, there's an implicit conversion to string here too, so it is your
    responsibility to make sure that items in `values` can be converted)
    """
    return sep.join([str(v) for v in values])
