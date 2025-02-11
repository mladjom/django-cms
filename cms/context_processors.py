from .models import SiteSettings

def site_settings(request):
    """Adds site settings as individual context variables"""
    settings = SiteSettings.get_instance()
    return {
        "site_name": settings.site_name,
        "site_description": settings.site_description,
        "site_tagline": settings.site_tagline,
        "blog_title": settings.blog_title,
        "blog_description": settings.blog_description,
        "blog_tagline": settings.blog_tagline,
        "blog_category_title": settings.blog_category_title,
        "blog_category_description": settings.blog_category_description,
        "blog_category_tagline": settings.blog_category_tagline,
        'GOOGLE_ANALYTICS_ID': settings.google_analytics_id if settings else ''
    }