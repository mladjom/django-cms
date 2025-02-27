from django.core.cache import cache
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.utils.translation import gettext as _
from django.views.generic import ListView
from ..models import Category, Post
from ..models import SiteSettings
from ..views.mixins import BaseMixin, BreadcrumbsMixin, SchemaMixin, SEOMetadataMixin, ViewCountMixin
import json
from django.shortcuts import get_object_or_404

@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class CategoryListView(BaseMixin, SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'
    paginate_by = 6
    page_kwarg = 'page'
    
    def get_queryset(self):
        cache_key = 'category_list_with_post_count'
        cached_queryset = cache.get(cache_key)
        
        if not cached_queryset:
            cached_queryset = list(
                Category.objects.annotate(
                    post_count=Count('posts', filter=Q(posts__in=Post.objects.active()))
                ).filter(
                    post_count__gt=0
                ).order_by('name')
            )
            cache.set(cache_key, cached_queryset, 3600)  # 1-hour cache
        
        return cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginate_base_url = reverse('category_list')
        context.update({
            'paginate_base_url': paginate_base_url,
            'schema': json.dumps(self.get_schema()),
            'schema_breadcrumbs': json.dumps(self.get_schema_breadcrumbs())
        })
        
        return context

    def get_schema(self):
        site_settings = SiteSettings.get_settings()
        schema = {
            **self.get_base_schema(),
            "@type": "CollectionPage",
            "name": site_settings.blog_category_tagline,
            "description": site_settings.blog_category_description,
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": len(self.get_queryset()),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": idx + 1,
                        "url": self.request.build_absolute_uri(category.get_absolute_url()),
                        "name": category.name,
                        "description": category.meta_description,
                    }
                    for idx, category in enumerate(self.get_queryset())
                ]
            }
        }
        return schema

    def get_meta_title(self):
        site_settings = SiteSettings.get_settings()
        return site_settings.blog_category_title
    
    def get_meta_description(self):
        site_settings = SiteSettings.get_settings()
        return site_settings.blog_category_description

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': _('Categories'), 'url': reverse('category_list')})
        return breadcrumbs

class CategoryView(ViewCountMixin, SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    model = Category
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 6
    page_kwarg = 'page'

    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.active().filter(
            category=self.category
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-created_at')


    def get_object(self):
        return self.category

    def get_schema(self):
        schema = {
            **self.get_base_schema(),
            "@type": "CollectionPage",
            "name": str(_('Posts in %(category_name)s') % {'category_name': self.category.name}),  # Convert __proxy__ to string
            "description": self.category.meta_description,
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
        context['category'] = self.category 
        context['paginate_base_url'] = reverse('category_posts', kwargs={'slug': self.category.slug})
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
        return context

    def get_meta_title(self):
        """Override to provide meta title based on the category"""
        return getattr(self.category, 'meta_title', None) or self.category.name or 'Category'

    def get_meta_description(self):
        """Override to provide meta description based on the category"""
        return getattr(self.category, 'meta_description', None) or f"Posts in {self.category.description}" or ''
        
    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.extend([
            {'name': _('Categories'), 'url': reverse('category_list')},
            {'name': self.category.name, 'url': self.category.get_absolute_url()}
        ])
        return breadcrumbs