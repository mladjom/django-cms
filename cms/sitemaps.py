from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Page, Post, Category, Tag

class StaticSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'contact',
            'post_list',
            'category_list',
        ]

    def location(self, item):
        return reverse(item)

class PostSitemap(Sitemap):
    """Sitemap for blog posts"""
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status=1)

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    """Sitemap for blog categories"""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()

class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return reverse('tagged', kwargs={'slug': obj.slug})

class PageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Page.objects.filter(status=1)  # Only published pages

    def location(self, obj):
        return reverse('page', kwargs={'slug': obj.slug})

# Combine sitemaps
sitemaps = {
    'static': StaticSitemap,
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'pages': PageSitemap,
}