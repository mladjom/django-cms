from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from cms.models import Post, Tag
from cms.views.mixins import SEOMetadataMixin, SchemaMixin, BreadcrumbsMixin, ViewCountMixin
import json

class TagView(ViewCountMixin, SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    template_name = 'blog/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 3 
    page_kwarg = 'page'
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(
            tags=self.tag,
            status=1
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-created_at')

    def get_object(self):
        return self.tag

    def get_schema(self):
        schema = {
            **self.get_base_schema(),
            "@type": "CollectionPage",
            "name": str(_('Posts tagged with %(tag_name)s') % {'tag_name': self.tag.name}),  # Convert __proxy__ to string
            "description": self.tag.meta_description,
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": [
                    {
                        "@type": "BlogPosting",
                        "position": idx + 1,
                        "url": self.request.build_absolute_uri(post.get_absolute_url()),
                        "headline": post.title,
                        "datePublished": post.created_at.isoformat(),
                        "author": {
                            "@type": "Person",
                            "name": post.author.get_full_name() or post.author.username
                        }
                    }
                    for idx, post in enumerate(self.get_queryset())  # Use get_queryset instead
                ]
            }
        }
        return schema
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag 
        context['pagination_base_url'] = f"tag/{self.tag.slug}"  # Base URL for pagination
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
        return context    

    def get_meta_title(self):
        """Override to provide meta title based on the tag"""
        return getattr(self.tag, 'meta_title', None) or self.tag.name or 'Tag'

    def get_meta_description(self):
        """Override to provide meta description based on the tag"""
        return getattr(self.tag, 'meta_description', None) or f"Posts in {self.tag.description}" or ''

    
    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.extend([
            {'name': _('Tag'), 'url': '#'},
            {'name': self.tag.name, 'url': self.tag.get_absolute_url()}
        ])                
        return breadcrumbs