from django.db import models
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class SiteSettings(models.Model):
    site_name = models.CharField(
        max_length=100,
        default="Website",
        verbose_name=_("Site Name")
    )
    site_description = models.TextField(
        default="A flexible content management platform.",
        verbose_name=_("Site Description")
    )
    site_tagline = models.CharField(
        max_length=255,
        default="Your online presence, simplified.",
        verbose_name=_("Site Tagline")
    )

    blog_title = models.CharField(
        max_length=100,
        default="Blog",
        verbose_name=_("Blog Title")
    )
    blog_description = models.TextField(
        default="Latest posts and updates.",
        verbose_name=_("Blog Description")
    )
    blog_tagline = models.CharField(
        max_length=200,
        default="Insights & Stories",
        verbose_name=_("Blog Tagline")
    )
    blog_category_title = models.CharField(
        max_length=100,
        default="Topics",
        verbose_name=_("Category Title")
    )
    blog_category_description = models.TextField(
        default="Explore posts by category.",
        verbose_name=_("Category Description")
    )
    blog_category_tagline = models.CharField(
        max_length=200,
        default="Find what interests you.",
        verbose_name=_("Category Tagline")
    )
    
    class Meta:
        verbose_name_plural = _('Settings')
        
    @classmethod
    def load(cls):
        """
        Loads the single SiteSettings instance.
        """
        try:
            return cls.objects.get(pk=1)
        except cls.DoesNotExist:
            return cls()

    @classmethod
    def get_instance(cls):
        """
        Gets the SiteSettings instance, ensuring it exists.
        """
        instance = cls.load()
        instance.save()  # Create or save the instance
        return instance

    @classmethod
    def get_settings(cls):
        """
        Gets the SiteSettings instance from the cache.
        """
        cache_key = 'site_settings'
        settings = cache.get(cache_key)

        if not settings:
            settings = cls.get_instance()
            cache.set(cache_key, settings, 3600)  # Cache for 1 hour

        return settings

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Invalidate cache on save
        cache.delete('site_settings')

    def delete(self, *args, **kwargs):
        raise ValueError("Deletion of the SiteSettings instance is not allowed.")

@receiver(post_save, sender=SiteSettings)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """
    Invalidates the cache on SiteSettings save.
    """
    cache.delete('site_settings')  
        
      
#singleton pattern to ensure there's only one SiteSettings instance