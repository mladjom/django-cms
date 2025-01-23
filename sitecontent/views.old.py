from datetime import timezone
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from .models import Category, Tag, Post, Page


class SchemaMixin:
    """Mixin for handling JSON-LD schema data"""
    
#     def get_schema(self):
#         raise NotImplementedError("Subclasses must implement get_schema()")

#     def get_base_schema(self):
#         return {
#             "@context": "https://schema.org",
#             "url": self.request.build_absolute_uri(),
#             "dateModified": timezone.now().isoformat()
#         }
    
#     def get_schema_breadcrumbs(self):
#         breadcrumbs = self.get_breadcrumbs()
#         schema = {
#             "@context": "https://schema.org",
#             "@type": "BreadcrumbList",
#             "itemListElement": []
#         }
        
#         for i, item in enumerate(breadcrumbs, start=1):
#             schema["itemListElement"].append({
#                 "@type": "ListItem",
#                 "position": i,
#                 "name": item['name'],
#                 "item": self.request.build_absolute_uri(item['url'])
#             })
#         return schema 





class SEOMetadataMixin:
    """Mixin to handle SEO metadata"""
    
#     def get_meta_title(self):
#         """Override in child classes to provide specific meta title"""
#         return getattr(self.object, 'meta_title', None) or getattr(self.object, 'title', '')
    
#     def get_meta_description(self):
#         """Override in child classes to provide specific meta description"""
#         return getattr(self.object, 'meta_description', None) or ''
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['meta_title'] = self.get_meta_title()
#         context['meta_description'] = self.get_meta_description()
#         return context





class PostListView(SEOMetadataMixin, BreadcrumbsMixin, SchemaMixin, ListView):
    model = Post
    paginate_by = 10
    context_object_name = 'posts'
    template_name = 'blog/post_list.html'
    
#     def get_queryset(self):
#         return Post.objects.filter(
#             status=1  # Published posts only
#         ).select_related(
#             'author', 'category'
#         ).prefetch_related(
#             'tags'
#         ).order_by('-created_at')
 
#     def get_schema(self):
#         schema = {
#             **self.get_base_schema(),
#             "@type": "Blog",
#             "name": "Blog Posts",
#             "description": "Latest blog posts",
#             "blogPost": [
#                 {
#                     "@type": "BlogPosting",
#                     "headline": post.title,
#                     "url": self.request.build_absolute_uri(post.get_absolute_url()),
#                     "datePublished": post.created_at.isoformat(),
#                     "dateModified": post.updated_at.isoformat(),
#                     "author": {
#                         "@type": "Person",
#                         "name": post.author.get_full_name() or post.author.username
#                     }
#                 }
#                 for post in self.get_context_data()['posts'][:5]  # Include first 5 posts
#             ]
#         }
#         return schema 
 
 
    
#     def get_meta_title(self):
#         return _('Blog Posts')
    
#     def get_meta_description(self):
#         return _('Latest blog posts and articles')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['schema'] = json.dumps(self.get_schema())
#         context['schema_breadcrumbs'] = json.dumps(self.get_schema_breadcrumbs())
#         context['featured_posts'] = Post.objects.filter(
#         status=1, is_featured=True
#         ).order_by('-created_at')[:5]
#         return context

class CategoryListView(SEOMetadataMixin, BreadcrumbsMixin, ListView):
    model = Category
    paginate_by = 10
    context_object_name = 'categories'
    template_name = 'blog/category_list.html'
    
#     def get_meta_title(self):
#         return _('Categories')

#     def get_meta_description(self):
#         return _('All categories')
    
class CategoryView(SEOMetadataMixin, BreadcrumbsMixin, ViewCountMixin, ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    
#     def get_queryset(self):
#         self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
#         return Post.objects.filter(
#             category=self.category,
#             status=1
#         ).select_related('author', 'category')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['category'] = self.category
#         return context
    
#     def get_breadcrumbs(self):
#         return super().get_breadcrumbs() + [
#             {'title': _('Categories'), 'url': reverse('category_list')},
#             {'title': self.category.name, 'url': self.category.get_absolute_url()}
#         ]


class TagView(SEOMetadataMixin, BreadcrumbsMixin, ViewCountMixin, ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/tag_posts.html'
    context_object_name = 'posts'
    
#     def get_queryset(self):
#         self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
#         return Post.objects.filter(
#             tags=self.tag,
#             status=1
#         ).select_related('author', 'category')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['tag'] = self.tag
#         return context
    
#     def get_breadcrumbs(self):
#         return super().get_breadcrumbs() + [
#             {'title': self.tag.name, 'url': self.tag.get_absolute_url()}
#         ]


class PostDetailView(SchemaMixin, SEOMetadataMixin, BreadcrumbsMixin, ViewCountMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
#     def get_queryset(self):
#         return Post.objects.filter(status=1).select_related('author', 'category').prefetch_related('tags')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
        
#         # Get previous and next posts
#         context['previous_post'] = Post.objects.filter(
#             status=1,
#             created_at__lt=self.object.created_at
#         ).order_by('-created_at').first()
        
#         context['next_post'] = Post.objects.filter(
#             status=1,
#             created_at__gt=self.object.created_at
#         ).order_by('created_at').first()
        
#         # Get related posts (same category or tags)
#         related_posts = Post.objects.filter(status=1).exclude(id=self.object.id)
#         related_posts = related_posts.filter(
#             category=self.object.category
#         ).union(
#             related_posts.filter(tags__in=self.object.tags.all())
#         ).distinct()[:3]
#         context['related_posts'] = related_posts
        
#         return context
    
#     def get_breadcrumbs(self):
#         return super().get_breadcrumbs() + [
#             {'title': self.object.category.name, 'url': self.object.category.get_absolute_url()},
#             {'title': self.object.title, 'url': self.object.get_absolute_url()}
#         ]
    
#     def get_schema_data(self):
#         return {
#             "@context": "https://schema.org",
#             "@type": "BlogPosting",
#             "headline": self.object.title,
#             "author": {
#                 "@type": "Person",
#                 "name": self.object.author.get_full_name() or self.object.author.username
#             },
#             "datePublished": self.object.created_at.isoformat(),
#             "dateModified": self.object.updated_at.isoformat(),
#             "mainEntityOfPage": {
#                 "@type": "WebPage",
#                 "@id": self.request.build_absolute_uri(self.object.get_absolute_url())
#             }
#         }


# class PageView(SEOMetadataMixin, BreadcrumbsMixin, ViewCountMixin, DetailView):
#     model = Page
#     template_name = 'blog/page.html'
#     context_object_name = 'page'
    
#     def get_breadcrumbs(self):
#         return super().get_breadcrumbs() + [
#             {'title': self.object.title, 'url': self.object.get_absolute_url()}
#         ]
        
# class PageView(DetailView):
#     model = Page
#     template_name = 'page.html'
#     context_object_name = 'page'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['breadcrumbs'] = [
#             {'url': '/', 'title': 'Home'},
#             {'url': self.object.get_absolute_url(), 'title': self.object.title}
#         ]

#         # Increase view count
#         self.object.view_count += 1
#         self.object.save()

#         # Generate JSON-LD schema
#         schema = {
#             "@context": "https://schema.org/",
#             "@type": "WebPage",
#             "headline": self.object.title,
#             "description": self.object.content[:160], 
#             "url": self.request.build_absolute_uri(),
#         }
#         context['schema'] = json.dumps(schema, cls=DjangoJSONEncoder)

#         return context    
 
class BreadcrumbsMixin:
    def get_breadcrumbs(self):
        breadcrumbs = [{'title': 'Home', 'url': reverse('home')}]
        current = self.object
        
        while current:
            breadcrumbs.append({
                'title': current.title,
                'url': current.get_absolute_url()
            })
            current = current.parent
            
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class ViewCountMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.view_count = F('view_count') + 1
        obj.save()
        obj.refresh_from_db()
        return obj 
    
class PageView(BreadcrumbsMixin, ViewCountMixin, DetailView):
    model = Page
    template_name = "page.html"
    context_object_name = "page"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.object

        # Generate breadcrumbs
        breadcrumbs = [
            {"name": "Home", "url": "/"},
            {"name": page.title, "url": self.request.path},
        ]
        context["breadcrumbs"] = breadcrumbs

        # JSON-LD schema
        json_ld = {
            "@context": "http://schema.org",
            "@type": "WebPage",
            "name": page.title,
            "url": self.request.build_absolute_uri(),
            "breadcrumb": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "/"},
                {"@type": "ListItem", "position": 2, "name": page.title, "item": self.request.build_absolute_uri()},
            ],
            "interactionStatistic": {
                "@type": "InteractionCounter",
                "interactionType": {"@type": "http://schema.org/InteractionType", "name": "ViewAction"},
                "userInteractionCount": page.view_count,
            },
        }
        context["json_ld"] = json_ld

        return context    