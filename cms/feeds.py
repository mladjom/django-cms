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
    def __init__(self):
        super().__init__()
        try:
            self.site_settings = SiteSettings.get_settings()
        except:
            self.site_settings = None

    def item_pubdate(self, item):
        return item.created_at
    
    def item_updateddate(self, item):
        return item.updated_at

    def description(self):
        return self.site_settings.site_description if self.site_settings else _("Blog feed")

    def item_categories(self, item):
        categories = [item.category.name]
        tags = [tag.name for tag in item.tags.all()]
        return categories + tags

    def get_image_url(self, image_field):
        if not image_field or not hasattr(image_field, 'url') or not self.site_settings:
            return None
        base_url, ext = str(image_field.url).rsplit('.', 1)
        largest_size = max(self.site_settings.image_sizes)
        return f"{base_url}-{largest_size}w.webp"

    def item_enclosure_url(self, item):
        if not self.site_settings:
            return None
        featured_image_url = item.get_featured_image_url()
        if featured_image_url:
            base_url, ext = str(featured_image_url).rsplit('.', 1)
            largest_size = max(self.site_settings.image_sizes)
            webp_url = f"{base_url}-{largest_size}w.webp"
            return self.request.build_absolute_uri(webp_url) if hasattr(self, 'request') else webp_url
        return None

    def item_enclosure_length(self, item):
        if not item.featured_image or not self.site_settings:
            return 0
        try:
            featured_image_url = item.get_featured_image_url()
            if featured_image_url:
                base_url, ext = str(featured_image_url).rsplit('.', 1)
                largest_size = max(self.site_settings.image_sizes)
                webp_path = f"{base_url}-{largest_size}w.webp"
                return os.path.getsize(webp_path) if os.path.exists(webp_path) else 0
        except:
            return 0
        return 0

    def item_enclosure_mime_type(self, item):
        return 'image/webp' if item.featured_image else None

    def get_feed(self, obj, request):
        self.request = request
        return super().get_feed(obj, request)

class BlogFeed(ExtendedRSSFeed):
    def title(self):
        return self.site_settings.blog_title if self.site_settings else _("Blog")
    
    def description(self):
        return self.site_settings.blog_description if self.site_settings else _("Blog posts")
    
    def link(self):
        return reverse('post_list')
    
    def items(self):
        return Post.objects.active().order_by('-created_at')[:20]
    
    def item_title(self, item):
        return item.meta_title or item.title
    
    def item_description(self, item):
        if item.excerpt:
            return item.excerpt
        soup = BeautifulSoup(item.content, 'html.parser')
        for img in soup.find_all('img'):
            img.replace_with(f"[Image: {img['alt']}]" if img.get('alt') else '')
        return soup.get_text()[:200]
    
    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username

class CategoryFeed(ExtendedRSSFeed):
    def get_object(self, request, slug):
        self.request = request
        return Category.objects.get(slug=slug)
    
    def title(self, obj):
        blog_title = self.site_settings.blog_title if self.site_settings else _("Blog")
        return f"{blog_title} - {obj.name}"
    
    def description(self, obj):
        if obj.description:
            return obj.description
        return self.site_settings.blog_category_description if self.site_settings else _("Category posts")
    
    def link(self, obj):
        return reverse('category_posts', args=[obj.slug])
    
    def items(self, obj):
        return Post.objects.active().filter(category=obj).order_by('-created_at')[:20]
    
    def item_title(self, item):
        return item.meta_title or item.title
    
    def item_description(self, item):
        if item.excerpt:
            return item.excerpt
        soup = BeautifulSoup(item.content, 'html.parser')
        for img in soup.find_all('img'):
            img.replace_with(f"[Image: {img['alt']}]" if img.get('alt') else '')
        return soup.get_text()[:200]
    
    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username

class BlogAtomFeed(BlogFeed):
    feed_type = Atom1Feed
    def subtitle(self):
        return self.description()

class CategoryAtomFeed(CategoryFeed):
    feed_type = Atom1Feed
    def subtitle(self, obj):
        return self.description(obj)