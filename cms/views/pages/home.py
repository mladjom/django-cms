import json
from django.views.generic import TemplateView
from cms.models import Post, Category
from django.db.models import Count, Q
from cms.views.mixins import SEOMetadataMixin, SchemaMixin
from ...models import SiteSettings

class HomeView(SEOMetadataMixin, SchemaMixin, TemplateView):
    #model = Post
    template_name = 'site/home.html' 
    #context_object_name = 'posts'

    def get_featured_posts(self):
        return Post.objects.active().filter(
            is_featured=True
        ).select_related('author', 'category').prefetch_related('tags')[:5]

    def get_schema(self):
        site_settings = SiteSettings.objects.first()
        schema = {
            **self.get_base_schema(),
            "@type": "WebPage",
            "name": site_settings.site_name,
            "description": site_settings.site_description,
            "headline": site_settings.site_tagline,
            "mainEntity": {
                 "@type": "ItemList",
                "itemListElement": [
                    {
                        "@type": "BlogPosting",
                        "headline": post.title,
                        "description": post.excerpt or '',
                        "url": self.request.build_absolute_uri(post.get_absolute_url())
                    } for post in self.get_featured_posts()[:3]
                ]      
            }
        }
        return schema
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Optimize queries with select_related and prefetch_related
        featured_posts = self.get_featured_posts()
        
        latest_posts = Post.objects.active().select_related(
            'author', 'category'
        ).prefetch_related('tags').order_by('-created_at')[:4]
        
        popular_posts = Post.objects.active().select_related(
            'author', 'category'
        ).prefetch_related('tags').order_by('-view_count')[:6]
        
        categories = Category.objects.annotate(
            post_count=Count(
                'posts', 
                filter=Q(posts__in=Post.objects.active())  # Use the active() method to filter published posts
            )
        ).order_by('-post_count')[:6]
        
        context.update({
            'featured_posts': featured_posts,
            'latest_posts': latest_posts,
            'popular_posts': popular_posts,
            'categories': categories,
            'schema': json.dumps(self.get_schema()),
            'meta_title': self.get_meta_title(),
            'meta_description': self.get_meta_description(),
        })
        
        return context

    def get_meta_title(self):
        site_settings = SiteSettings.objects.first()        
        return str(site_settings.site_tagline)
    
    def get_meta_description(self):
        site_settings = SiteSettings.objects.first()        
        return str(site_settings.site_description)