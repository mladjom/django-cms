from django.db import models
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
import json

def default_image_sizes():
    return [576, 768, 992, 1200]

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

    # Image Settings
    image_sizes = models.JSONField(
        default=default_image_sizes,
        verbose_name=_("Image Sizes"),
        help_text=_("List of image sizes for responsive images (in pixels)")
    )

    image_webp_quality = models.IntegerField(
        default=85,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name=_("WebP Quality"),
        help_text=_("WebP compression quality (1-100)")
    )
    image_aspect_ratio_width = models.IntegerField(
        default=16,
        validators=[MinValueValidator(1)],
        verbose_name=_("Aspect Ratio Width"),
        help_text=_("Aspect ratio width value")
    )
    image_aspect_ratio_height = models.IntegerField(
        default=9,
        validators=[MinValueValidator(1)],
        verbose_name=_("Aspect Ratio Height"),
        help_text=_("Aspect ratio height value")
    )
    image_upload_path_format = models.CharField(
        max_length=255,
        default="{model_name}s/{year}/{month}/{day}",
        verbose_name=_("Upload Path Format"),
        help_text=_("Format string for upload path. Available variables: {model_name}, {year}, {month}, {day}")
    )
    
    class Meta:
        verbose_name = _('Settings')
        verbose_name_plural = _('Settings')

    # def get_image_settings(self):
    #     """Returns image settings in the original dictionary format"""
    #     return {
    #         'SIZES': self.image_sizes,
    #         'WEBP_QUALITY': self.image_webp_quality,
    #         'ASPECT_RATIO': (self.image_aspect_ratio_width, self.image_aspect_ratio_height),
    #         'UPLOAD_PATH_FORMAT': self.image_upload_path_format
    #     }

    def __str__(self):
        return self.site_name  
            
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