from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext as _
from ..models import Post
from ..models import SiteSettings
from ..views.mixins import SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ViewCountMixin
import json

class PostListView(SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    page_kwarg = 'page'
    
    def get_queryset(self):
        return (
            self.model.objects.active()  # Use the active() method from PostManager
            .select_related('author', 'category')  # Optimize related fields
            .prefetch_related('tags')  # Optimize many-to-many fields
            .order_by('-created_at')  # Order by creation date
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginate_base_url = reverse('post_list')
        
        context.update({
            'paginate_base_url': paginate_base_url,
            'schema': json.dumps(self.get_schema()),
            'schema_breadcrumbs': json.dumps(self.get_schema_breadcrumbs())
        })
        
        return context
    
    def get_schema(self):
        site_settings = SiteSettings.get_settings()
        posts = self.get_queryset()[:5]  # Evaluate queryset once
        schema = {
            **self.get_base_schema(),
            "@type": "Blog",
            "name": site_settings.blog_title,
            "description": site_settings.blog_description,
            "blogPost": [
                {
                    "@type": "BlogPosting",
                    "headline": post.title,
                    "url": self.request.build_absolute_uri(post.get_absolute_url()),
                    "datePublished": post.created_at.isoformat(),
                    "dateModified": post.updated_at.isoformat(),
                    "author": {
                        "@type": "Person",
                        "name": post.author.get_full_name() or post.author.username
                    }
                }
                for post in posts
            ]
        }
        return schema

    def get_meta_title(self):
        site_settings = SiteSettings.get_settings()
        return str(site_settings.blog_title)

    def get_meta_description(self):
        site_settings = SiteSettings.get_settings()
        return str(site_settings.blog_description) 

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': str(_('Posts')), 'url': reverse('post_list')})
        return breadcrumbs

class PostDetailView(ViewCountMixin, SEOMetadataMixin, SchemaMixin, BreadcrumbsMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.active(
        ).select_related(
            'author', 'category'
        ).prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
                
        # Get related posts from same category
        context['related_posts'] = Post.objects.active().filter(
            category=post.category
        ).exclude(
            id=post.id
        ).order_by('-created_at')[:3]
        
        # Add previous/next post navigation
        context['previous_post'] = (
            Post.objects.active()  # Use the active() method to filter published posts
            .filter(created_at__lt=post.created_at)  # Filter posts created before the current post
            .order_by('-created_at')  # Order by creation date (newest first)
            .first()  # Get the first post in the filtered queryset
        )

        context['next_post'] = (
            Post.objects.active()  # Use the active() method to filter published posts
            .filter(created_at__gt=post.created_at)  # Filter posts created after the current post
            .order_by('created_at')  # Order by creation date (oldest first)
            .first()  # Get the first post in the filtered queryset
        )
            
        return context        
     
    def get_schema(self):
        post = self.get_object()
        schema = {
            **self.get_base_schema(),
            "@type": "BlogPosting",
            "headline": post.title,
            "description": post.meta_description or post.excerpt,
            "author": {
                "@type": "Person",
                "name": post.author.get_full_name() or post.author.username
            },
            "datePublished": post.created_at.isoformat(),
            "dateModified": post.updated_at.isoformat(),
            "articleBody": post.content,
            "keywords": [tag.name for tag in post.tags.all()],
            "articleSection": post.category.name
        }
        
        if post.featured_image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": self.request.build_absolute_uri(post.featured_image.url),
                "width": "1200",
                "height": "630"
            }
            
        return schema

    def get_breadcrumbs(self):
        post = self.get_object()
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.extend([
            {'name': _('Posts'), 'url': reverse('post_list')},
            {'name': post.title, 'url': post.get_absolute_url()}
        ])
        return breadcrumbs