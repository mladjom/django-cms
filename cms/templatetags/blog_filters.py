from django import template
import math
from django.utils.translation import gettext_lazy as _, ngettext
from django.utils.timezone import now
from datetime import timedelta

register = template.Library()

@register.filter
def reading_time(content):
    """
    Returns the estimated reading time for the given content.
    
       Usage: {{ post.content|reading_time }}
    """
    word_count = len(content.split())
    minutes = math.ceil(word_count / 200)  # Average reading speed
    return f"{minutes} {_('min read')}"

@register.filter
def relative_date(value):
    """
    Returns a humanized string representing time difference between now and the input date.
    
    Usage: {{ post.created_at|relative_date }}
    """
    if not value:
        return ''
    
    delta = now() - value

    if delta < timedelta(minutes=1):
        return _('Just now')
    elif delta < timedelta(hours=1):
        minutes = delta.seconds // 60
        return ngettext(
            '%(minutes)d minute ago',
            '%(minutes)d minutes ago',
            minutes
        ) % {'minutes': minutes}
    elif delta < timedelta(days=1):
        hours = delta.seconds // 3600
        return ngettext(
            '%(hours)d hour ago',
            '%(hours)d hours ago',
            hours
        ) % {'hours': hours}
    elif delta < timedelta(days=30):
        days = delta.days
        return ngettext(
            '%(days)d day ago',
            '%(days)d days ago',
            days
        ) % {'days': days}
    else:
        # For exact date, use a proper string format instead of a translation proxy object
        # Convert the translation proxy to a string first
        date_format = str(_('%B %d, %Y'))
        return value.strftime(date_format)
