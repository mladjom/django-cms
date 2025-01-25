from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.db import models
from django.db.models import F, Count
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from .models import Post, Category, Tag, Page
from django.utils.translation import gettext_lazy as _
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Explicitly set to INFO level if necessary

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class ViewCountMixin:
    """Mixin to handle view count incrementing for models"""

    def get_object(self, queryset=None):
        if not hasattr(self, '_object'):
            self._object = super().get_object(queryset)
            with atomic():
                try:
                    self._object.view_count = F('view_count') + 1
                    self._object.save(update_fields=['view_count'])
                    # print("Logger should trigger here")
                    # logger.info(f"View count incremented for {self._object.__class__.__name__} with ID: {self._object.pk}")
                except Exception as e:
                    logger.error(f"Failed to increment view count: {e}")
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
        return [{'name': 'Home', 'url': '/'}]
    
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
                "name": item['name'],
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
                "name": "Your Site Name",  # Replace with your actual site name
                "logo": {
                    "@type": "ImageObject",
                    "url": self.request.build_absolute_uri("/path/to/logo.png")  # Replace with your logo path
                }
            },
            "url": self.request.build_absolute_uri(),
            "datePublished": datetime.now().isoformat()
        } 
 
class HomeView(SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    model = Post
    template_name = 'site/home.html' 
    context_object_name = 'posts'

    def get_schema(self):
        schema = {
            **self.get_base_schema(),
            "@type": "Blog",
            "name": "Blog Posts",
            "description": "Latest blog posts",
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
                for post in self.get_queryset()[:5]  # Use get_queryset instead of get_context_data
            ]
        }
        return schema

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = Post.objects.filter(
            status=1, is_featured=True
        ).order_by('-created_at')[:3]
        context['schema'] = json.dumps(self.get_schema())
        return context

    def get_meta_title(self):
        return str(_('Home Title'))
    
    def get_meta_description(self):
        return str(_('Home Description'))
    
class PostListView(SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 3
    
    def get_queryset(self):
        return Post.objects.filter(
            status=1  # Published posts only
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-created_at')
 
    def get_schema(self):
        schema = {
            **self.get_base_schema(),
            "@type": "Blog",
            "name": "Blog Posts",
            "description": "Latest blog posts",
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
                for post in self.get_queryset()[:5]  # Use get_queryset instead of get_context_data
            ]
        }
        return schema
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = Post.objects.filter(
            status=1, is_featured=True
        ).order_by('-created_at')[:3]
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
        return context

    def get_meta_title(self):
        return str(_('Blog Posts'))
    
    def get_meta_description(self):
        return str(_('Latest blog posts and articles'))

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': str(_('Posts')), 'url': reverse('post_list')})
        return breadcrumbs

class CategoryListView(SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'
    paginate_by = 3
    
    def get_queryset(self):
        return Category.objects.annotate(
            post_count=Count('posts', filter=models.Q(posts__status=1))
        ).order_by('name')

    def get_schema(self):
        schema = {
            **self.get_base_schema(),
            "@type": "CollectionPage",
            "name": "Blog Categories",
            "description": "All blog categories",
            "hasPart": [
                {
                    "@type": "ItemList",
                    "name": category.name,
                    "url": self.request.build_absolute_uri(category.get_absolute_url()),
                    "numberOfItems": category.posts.filter(status=1).count()
                }
                for category in self.get_queryset()
            ]
        }
        return schema

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
        return context

    def get_meta_title(self):
        return str(_('Categories'))
    
    def get_meta_description(self):
        return str(_('All blog categories'))

    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': str(_('Categories')), 'url': reverse('category_list')})
        return breadcrumbs

class CategoryView(ViewCountMixin, SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    #paginate_by = 10
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            category=self.category,
            status=1
        ).select_related(
            'author', 'category'
        ).prefetch_related(
            'tags'
        ).order_by('-created_at')

    def get_schema(self):
        schema = {
            **self.get_base_schema(),
            "@type": "CollectionPage",
            "name": f"Posts in {self.category.name}",
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
        context['category'] = self.category  # Add category to context
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
        return context
        
    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.extend([
            {'name': 'Categories', 'url': reverse('category_list')},
            {'name': self.category.name, 'url': self.category.get_absolute_url()}
        ])
        return breadcrumbs

class TagView(ViewCountMixin, SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    template_name = 'blog/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
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

    def get_schema(self):
        schema = {
            **self.get_base_schema(),
            "@type": "CollectionPage",
            "name": f"Posts tagged with {self.tag.name}",
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
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
        return context    

    
    def get_breadcrumbs(self):
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': f'Tag: {self.tag.name}', 'url': self.tag.get_absolute_url()})
        return breadcrumbs

class PostDetailView(ViewCountMixin, SEOMetadataMixin, SchemaMixin, BreadcrumbsMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.filter(
            status=1
        ).select_related(
            'author', 'category'
        ).prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
                
        # Get related posts from same category
        context['related_posts'] = Post.objects.filter(
            category=post.category,
            status=1
        ).exclude(
            id=post.id
        ).order_by('-created_at')[:3]
        
        # Add previous/next post navigation
        context['prev_post'] = Post.objects.filter(
            status=1,
            created_at__lt=post.created_at
        ).order_by('-created_at').first()
        
        context['next_post'] = Post.objects.filter(
            status=1,
            created_at__gt=post.created_at
        ).order_by('created_at').first()
            
        return context        
    def get_breadcrumbs(self):
        post = self.get_object()
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.extend([
            {'name': 'Posts', 'url': reverse('post_list')},
            {'name': post.title, 'url': post.get_absolute_url()}
        ])
        return breadcrumbs        

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

class PageView(ViewCountMixin, SEOMetadataMixin,BreadcrumbsMixin, SchemaMixin, DetailView):
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
        context['schema'] = json.dumps(self.get_schema())
        context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
        return context
    
    def get_breadcrumbs(self):
        page = self.get_object()
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.append({'name': page.title, 'url': page.get_absolute_url()})
        return breadcrumbs