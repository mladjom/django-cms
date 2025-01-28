from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """Adds a CSS class to a form field widget."""
    if hasattr(field, 'field') and hasattr(field.field.widget, 'attrs'):
        existing_classes = field.field.widget.attrs.get('class', '')
        updated_classes = f"{existing_classes} {css_class}".strip()
        field.field.widget.attrs['class'] = updated_classes
    return field
