from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Category Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_('Meta Title'))
    meta_description = models.TextField(max_length=160, blank=True, verbose_name=_('Meta Description'))
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('View Count'))
    featured_image = models.ImageField(upload_to='uploads/', blank=True, verbose_name=_('Featured Image'))
    
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

class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Tag Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_('Meta Title'))
    meta_description = models.TextField(max_length=160, blank=True, verbose_name=_('Meta Description'))
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('View Count'))
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tagged', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

class Post(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name=_('Title'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='posts', verbose_name=_('Author'))
    content = models.TextField(verbose_name=_('Content'))
    excerpt = models.TextField(blank=True, verbose_name=_('Excerpt'))

    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_('Meta Title'))
    meta_description = models.TextField(max_length=160, blank=True, verbose_name=_('Meta Description'))

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts', verbose_name=_('Category'))
    tags = models.ManyToManyField(Tag, related_name='posts', verbose_name=_('Tags'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    status = models.IntegerField(choices=[(0, "Draft"), (1, "Published")], default=0, verbose_name=_('Status'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Is Featured'))

    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('View Count'))
    featured_image = models.ImageField(upload_to='uploads/', blank=True, verbose_name=_('Featured Image'))

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


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
