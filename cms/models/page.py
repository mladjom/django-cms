from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class Page(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name=_('Title'))
    slug = models.SlugField(max_length=250, unique=True, verbose_name=_('Slug'))
    content = models.TextField(verbose_name=_('Content'))
    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_('Meta Title'))
    meta_description = models.TextField(max_length=160, blank=True, verbose_name=_('Meta Description'))
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('View Count'))
    status = models.IntegerField(choices=[(0, "Draft"), (1, "Published")], default=0, verbose_name=_('Status'))

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Page, self).save(*args, **kwargs)
