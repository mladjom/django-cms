import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import logging
from PIL import Image
from datetime import datetime
from .settings import SiteSettings

logger = logging.getLogger(__name__)

def calculate_height(width, aspect_ratio=None):
    """Calculate height based on width and aspect ratio."""
    site_settings = SiteSettings.get_settings()
    if aspect_ratio is None:
        aspect_ratio = (site_settings.image_aspect_ratio_width, site_settings.image_aspect_ratio_height)
    return int(width * (aspect_ratio[1] / aspect_ratio[0]))

def resize_and_compress_images(image_path, base_path, base_filename, sizes=None, quality=None, aspect_ratio=None):
    """Resize and compress an image into multiple sizes."""
    site_settings = SiteSettings.get_settings()
    sizes = sizes or site_settings.image_sizes
    quality = quality or site_settings.image_webp_quality
    aspect_ratio = aspect_ratio or (site_settings.image_aspect_ratio_width, site_settings.image_aspect_ratio_height)

    try:
        logger.info(f"Processing image: {image_path}")

        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')

            results = []
            for width in sizes:
                height = calculate_height(width, aspect_ratio)
                resized_img = img.copy()
                resized_img.thumbnail((width, height), Image.LANCZOS)
                new_filename = f"{base_filename}-{width}x{height}.webp"
                new_path = os.path.join(base_path, new_filename)
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                resized_img.save(new_path, format='WEBP', quality=quality)
                logger.info(f"Saved resized image: {new_path}")
                results.append(new_path)
        return results
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        return []

def image_upload_path(instance, filename):
    """Generate dynamic upload path for images."""
    site_settings = SiteSettings.get_settings()
    model_name = instance.__class__.__name__.lower()
    return os.path.join(
        site_settings.image_upload_path_format.format(
            model_name=model_name,
            year=datetime.now().strftime('%Y'),
            month=datetime.now().strftime('%m'),
            day=datetime.now().strftime('%d'),
        ),
        filename
    )
    
class FeaturedImageModel(models.Model):
    featured_image = models.ImageField(
        upload_to=image_upload_path,  
        blank=True,
        null=True,
        verbose_name=_("Featured Image")
    )

    class Meta:
        abstract = True

    @property
    def image_sizes(self):
        """Define the required image sizes"""
        site_settings = SiteSettings.get_settings()
        return site_settings.image_sizes

    def get_image_variants(self):
        """Get all image variants paths"""
        if not self.featured_image:
            return {}
        
        variants = {}
        original_name = os.path.basename(self.featured_image.name)
        # Keep the full filename except dimensions and extension
        base_name = '-'.join(original_name.split('-')[:-1]) if '-' in original_name else original_name.split('.')[0]
 
        site_settings = SiteSettings.get_settings()
        aspect_ratio = (site_settings.image_aspect_ratio_width, site_settings.image_aspect_ratio_height)
                
        for width in self.image_sizes:
            height = self.calculate_height(width, aspect_ratio)
            filename = f"{base_name}-{width}x{height}.webp"
            relative_path = os.path.join(os.path.dirname(self.featured_image.name), filename)
            variants[width] = {
                'url': f"{settings.MEDIA_URL}{relative_path}",
                #'path': os.path.join(base_path, filename),
                'path': os.path.join(settings.MEDIA_ROOT, relative_path)

            }
        return variants

    def handle_old_featured_image(self):
        """Handle deletion of old featured image and its variants"""
        if self.pk:
            try:
                old_instance = type(self).objects.get(pk=self.pk)
                if old_instance.featured_image and old_instance.featured_image != self.featured_image:
                    # Remove main image
                    try:
                        if os.path.exists(old_instance.featured_image.path):
                            os.remove(old_instance.featured_image.path)
                    except Exception as e:
                        logger.error(f"Error removing original image: {e}")

                    # Remove all variants
                    for variant in old_instance.get_image_variants().values():
                        try:
                            if os.path.exists(variant['path']):
                                os.remove(variant['path'])
                        except Exception as e:
                            logger.error(f"Error removing variant: {e}")
            except type(self).DoesNotExist:
                pass

    def process_featured_image(self):
        """Process the featured image and create all required sizes"""
        if not self.featured_image:
            return

        # Allow model-specific image processing
        if hasattr(self, 'process_model_specific_image'):
            self.process_model_specific_image()
            return

        # Default multi-size processing
        slug_source = getattr(self, 'name', None) or getattr(self, 'title', None) or 'default'
        base_filename = slugify(slug_source)
        
        original_path = self.featured_image.path
        base_path = os.path.dirname(original_path)
        
        site_settings = SiteSettings.get_settings()
        aspect_ratio = (site_settings.image_aspect_ratio_width, site_settings.image_aspect_ratio_height)
        
        results = resize_and_compress_images(
            image_path=original_path,
            base_path=base_path,
            base_filename=base_filename,
            sizes=self.image_sizes,
            quality=site_settings.image_webp_quality,
            aspect_ratio=aspect_ratio
        )
        
        if results:
            largest_size = max(self.image_sizes)
            largest_height = calculate_height(largest_size, aspect_ratio)
            main_filename = f"{base_filename}-{largest_size}x{largest_height}.webp"
            new_main_path = os.path.join(base_path, main_filename)
            
            if original_path != new_main_path and os.path.exists(original_path):
                os.remove(original_path)
            
            # Update the field with relative path
            relative_path = os.path.relpath(new_main_path, settings.MEDIA_ROOT)
            self.featured_image.name = relative_path

    def save(self, *args, **kwargs):
        """Save the model and process images"""
        is_new_instance = self.pk is None
        
        # Handle old image replacement
        if not is_new_instance:
            self.handle_old_featured_image()

        # Save instance first to apply upload_to logic
        super().save(*args, **kwargs)

        # Process the featured image after initial save
        if self.featured_image:
            self.process_featured_image()
            super().save(update_fields=['featured_image'])

    def delete(self, *args, **kwargs):
        """Delete all image variants when the model instance is deleted"""
        if self.featured_image:
            # Delete all image variants
            for variant in self.get_image_variants().values():
                try:
                    if os.path.exists(variant['path']):
                        os.remove(variant['path'])
                except Exception as e:
                    logger.error(f"Error deleting variant: {e}")

            # Delete original image
            try:
                if os.path.exists(self.featured_image.path):
                    os.remove(self.featured_image.path)
            except Exception as e:
                logger.error(f"Error deleting original image: {e}")

        super().delete(*args, **kwargs)

    def calculate_height(self, width, aspect_ratio=None):
        """Calculate height based on width and aspect ratio."""
        site_settings = SiteSettings.get_settings()
        if aspect_ratio is None:
            aspect_ratio = (site_settings.image_aspect_ratio_width, site_settings.image_aspect_ratio_height)
        return int(width * (aspect_ratio[1] / aspect_ratio[0]))