from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .featured_image import FeaturedImageModel

class Category(FeaturedImageModel, models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Category Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_('Meta Title'))
    meta_description = models.TextField(max_length=160, blank=True, verbose_name=_('Meta Description'))
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('View Count'))
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
            
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_posts', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)