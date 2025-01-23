from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def as_json(value):
    """
    Renders JSON string as safe HTML without escaping
    Usage: {{ schema|as_json }}
    """
    return mark_safe(value)
