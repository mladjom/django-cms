from .settings import APP_SETTINGS

def app_settings(request):
    """
    Exposes app-specific settings to all templates.
    """
    return {
        'site_name': APP_SETTINGS.get('NAME', 'Default Site Name'),
        'site_tagline': APP_SETTINGS.get('TAGLINE', ''),
    }