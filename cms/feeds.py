from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.feedgenerator import Atom1Feed
from .models.settings import SiteSettings
from .models.post import Post
from .models.category import Category  
from django.contrib.sites.shortcuts import get_current_site
from bs4 import BeautifulSoup
import os

class ExtendedRSSFeed(Feed):
    """Base RSS feed with site settings integration"""
    
    def __init__(self):
        super().__init__()
        self.site_settings = SiteSettings.get_settings()

    def item_pubdate(self, item):
        return item.created_at
    
    def item_updateddate(self, item):
        return item.updated_at

    def description(self):
        return self.site_settings.site_description

    def item_categories(self, item):
        categories = [item.category.name]
        tags = [tag.name for tag in item.tags.all()]
        return categories + tags

    def get_image_url(self, image_field):
        """Get the largest size WebP version of the image"""
        if not image_field:
            return None
            
        if not hasattr(image_field, 'url'):
            return None
            
        base_url, ext = str(image_field.url).rsplit('.', 1)
        largest_size = max(self.site_settings.image_sizes)
        return f"{base_url}-{largest_size}w.webp"

    def item_enclosure_url(self, item):
        featured_image_url = item.get_featured_image_url()
        if featured_image_url:
            # Get the base URL from the featured image
            base_url, ext = str(featured_image_url).rsplit('.', 1)
            
            # Use the largest available size for the feed
            largest_size = max(self.site_settings.image_sizes)
            webp_url = f"{base_url}-{largest_size}w.webp"
            
            if hasattr(self, 'request'):
                return self.request.build_absolute_uri(webp_url)
            return webp_url
        return None

    def item_enclosure_length(self, item):
        """Get the size of the WebP image"""
        if not item.featured_image:
            return 0
            
        try:
            featured_image_url = item.get_featured_image_url()
            if featured_image_url:
                base_url, ext = str(featured_image_url).rsplit('.', 1)
                largest_size = max(self.site_settings.image_sizes)
                webp_path = f"{base_url}-{largest_size}w.webp"
                
                if os.path.exists(webp_path):
                    return os.path.getsize(webp_path)
        except Exception as e:
            print(f"Error getting image size: {e}")
        return 0

    def item_enclosure_mime_type(self, item):
        if item.featured_image:
            return 'image/webp'
        return None

    def get_feed(self, obj, request):
        self.request = request
        return super().get_feed(obj, request)

class ExtendedAtomFeed(ExtendedRSSFeed):
    """Base Atom feed with site settings integration"""
    feed_type = Atom1Feed
    
    def subtitle(self):
        return self.description()

class BlogFeed(ExtendedRSSFeed):
    """Main blog RSS feed"""
    
    def title(self):
        return self.site_settings.blog_title
    
    def description(self):
        return self.site_settings.blog_description
    
    def link(self):
        return reverse('post_list')
    
    def items(self):
        return Post.objects.active().order_by('-created_at')[:20]
    
    def item_title(self, item):
        return item.meta_title or item.title
    
    def item_description(self, item):
        if item.excerpt:
            return item.excerpt
        
        # Clean HTML content
        soup = BeautifulSoup(item.content, 'html.parser')
        # Replace img tags with their alt text
        for img in soup.find_all('img'):
            if img.get('alt'):
                img.replace_with(f"[Image: {img['alt']}]")
            else:
                img.decompose()
        
        return soup.get_text()[:200]
    
    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username

    def item_extra_kwargs(self, item):
        """Additional feed item data"""
        return {
            'meta_description': item.meta_description,
            'meta_title': item.meta_title,
            'view_count': item.view_count,
            'is_featured': item.is_featured,
        }

class BlogAtomFeed(BlogFeed):
    """Main blog Atom feed"""
    feed_type = Atom1Feed
    
    def subtitle(self):
        return self.description()

class CategoryFeed(ExtendedRSSFeed):
    """RSS feed for specific blog categories"""
    
    def get_object(self, request, slug):
        self.request = request
        return Category.objects.get(slug=slug)
    
    def title(self, obj):
        return f"{self.site_settings.blog_title} - {obj.name}"
    
    def description(self, obj):
        return obj.description or self.site_settings.blog_category_description
    
    def link(self, obj):
        return reverse('category_posts', args=[obj.slug])
    
    def items(self, obj):
        return Post.objects.active().filter(
            category=obj
        ).order_by('-created_at')[:20]
    
    def item_title(self, item):
        return item.meta_title or item.title
    
    def item_description(self, item):
        if item.excerpt:
            return item.excerpt
            
        # Clean HTML content
        soup = BeautifulSoup(item.content, 'html.parser')
        # Replace img tags with their alt text
        for img in soup.find_all('img'):
            if img.get('alt'):
                img.replace_with(f"[Image: {img['alt']}]")
            else:
                img.decompose()
                
        return soup.get_text()[:200]
    
    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username

    def item_extra_kwargs(self, item):
        """Additional feed item data"""
        return {
            'meta_description': item.meta_description,
            'meta_title': item.meta_title,
            'view_count': item.view_count,
            'is_featured': item.is_featured,
            'category_name': item.category.name
        }

class CategoryAtomFeed(CategoryFeed):
    """Atom feed for specific blog categories"""
    feed_type = Atom1Feed
    
    def subtitle(self, obj):
        return self.description(obj)