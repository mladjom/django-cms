import json
from cms.models import Page
from cms.views.mixins import SEOMetadataMixin, SchemaMixin, BreadcrumbsMixin, ViewCountMixin
from django.views.generic import DetailView

class PageView(ViewCountMixin, SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, DetailView):
    model = Page 
    template_name = 'site/page.html'
    context_object_name = 'page'

    def get_schema(self):
        page = self.get_object()
        schema = {
            **self.get_base_schema(),
            "@type": "WebPage",
            "name": page.title,
            "description": page.meta_description,
            "mainEntityOfPage": self.request.build_absolute_uri(),
            "text": page.content
        }
        return schema
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'schema': json.dumps(self.get_schema()),
            'schema_breadcrumbs': json.dumps(self.get_schema_breadcrumbs()),
            'meta_title': self.get_meta_title(),
            'meta_description': self.get_meta_description()
        })
        return context
    
    def get_breadcrumbs(self):
        page = self.get_object()
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': page.title, 'url': page.get_absolute_url()})
        return breadcrumbs