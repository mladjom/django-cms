from .settings import SITE_SETTINGS, BLOG_SETTINGS

def app_settings(request):
    """
    Exposes app-specific settings to all templates.
    """
    return {
        'site_name': SITE_SETTINGS.get('NAME'),
        'site_tagline': SITE_SETTINGS.get('TAGLINE', ''),
        'site_description': SITE_SETTINGS.get('DESCRIPTION', ''),
        'site_url': SITE_SETTINGS.get('URL', ''),
        'site_logo': SITE_SETTINGS.get('LOGO', ''),
        'site_email': SITE_SETTINGS.get('EMAIL', ''),
        'blog_title': BLOG_SETTINGS.get('TITLE', 'Blog'),
        'blog_description': BLOG_SETTINGS.get('DESCRIPTION', ''),
        'blog_tagline': BLOG_SETTINGS.get('TAGLINE', ''),
        'category_title': BLOG_SETTINGS.get('CATEGORY', {}).get('TITLE', 'Categories'),
        'category_description': BLOG_SETTINGS.get('CATEGORY', {}).get('DESCRIPTION', ''),
        'category_tagline': BLOG_SETTINGS.get('CATEGORY', {}).get('TAGLINE', ''),
    }