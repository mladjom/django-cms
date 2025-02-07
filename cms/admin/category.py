from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .mixins import DeleteWithImageMixin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class CategoryAdmin(DeleteWithImageMixin, admin.ModelAdmin):
    list_display = ('name', 'post_count', 'view_count', 'display_featured_image')
    list_filter = ('view_count',)
    search_fields = ('name', 'meta_title')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('view_count', 'featured_image_preview')
    save_on_top = True
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug' 'description')
        }),
        (_('Featured Image'), {
            'fields': ('featured_image', 'featured_image_preview'),
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Publication Settings'), {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
    )     
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = _('Posts')
    
    def display_featured_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.featured_image.url)
        return ''
    display_featured_image.short_description = _('Image')

    def featured_image_preview(self, obj):
        if obj.featured_image:
            return mark_safe(f'<img src="{obj.featured_image.url}" style="max-width:200px; max-height:200px;" />')
        return 'No Image'
    featured_image_preview.short_description = _('Image Preview')    