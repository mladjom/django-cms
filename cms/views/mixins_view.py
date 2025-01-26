from cms.settings import SITE_SETTINGS
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.db.models import F
from django.db.transaction import atomic
from django.utils.translation import gettext as _
from datetime import datetime

class BaseMixin:
    @method_decorator(cache_page(60 * 15))  # 15-minute cache
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class ViewCountMixin:
    """Mixin to handle view count incrementing for models"""

    def get_object(self, queryset=None):
        if not hasattr(self, '_object'):
            self._object = super().get_object(queryset)
            with atomic():
                try:
                    self._object.view_count = F('view_count') + 1
                    self._object.save(update_fields=['view_count'])
                except Exception as e:
                    print(f"Failed to increment view count: {e}")
                    raise
                self._object.refresh_from_db()
        return self._object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()  # Single call to get_object
        return context

class SEOMetadataMixin:
    """Mixin to handle SEO metadata"""
    
    def get_meta_title(self):
        """Override in child classes to provide specific meta title"""
        title = getattr(self, 'object', None)
        if title:
            return getattr(title, 'meta_title', None) or getattr(title, 'title', '') or 'Untitled'
        return 'Page'
    
    def get_meta_description(self):
        """Override in child classes to provide specific meta description"""
        obj = getattr(self, 'object', None)
        return getattr(obj, 'meta_description', None) or getattr(obj, 'excerpt', '') or ''
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = self.get_meta_title()
        context['meta_description'] = self.get_meta_description()
        return context

class BreadcrumbsMixin:
    def get_breadcrumbs(self):
        return [{'name': str(_('Home')), 'url': '/'}]
    
    def get_schema_breadcrumbs(self):
        breadcrumbs = self.get_breadcrumbs()
        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        }
        
        for i, item in enumerate(breadcrumbs, start=1):
            schema["itemListElement"].append({
                "@type": "ListItem",
                "position": i,
                "name": str(item['name']),  # Convert __proxy__ to string
                "item": self.request.build_absolute_uri(item['url'])
            })
        return schema

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        context['schema_breadcrumbs'] = self.get_schema_breadcrumbs()
        return context
 
class SchemaMixin:
    """Mixin to provide base schema generation for different view types"""
    
    def get_base_schema(self):
        """
        Provide a base schema with common properties for all pages
        """
        return {
            "@context": "https://schema.org",
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self.request.build_absolute_uri()
            },
            "publisher": {
                "@type": "Organization",
                "name": SITE_SETTINGS['NAME'],  
                "logo": {
                    "@type": "ImageObject",
                    "url": self.request.build_absolute_uri(SITE_SETTINGS['LOGO'])
                }
            },
            "url": self.request.build_absolute_uri(),
            "datePublished": datetime.now().isoformat()
        } 