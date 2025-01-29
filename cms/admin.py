from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from .models import Category, Tag, Post, Page
from django_ace import AceWidget
from django import forms
import os

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'view_count')
    list_filter = ('view_count',)
    search_fields = ('name', 'meta_title')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('view_count',)
    save_on_top = True
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = _('Posts')
    


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'view_count')
    list_filter = ('view_count',)
    search_fields = ('name', 'meta_title')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('view_count',)
    save_on_top = True
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = _('Posts')

class PostForm(forms.ModelForm):
    # Use AceWidget for the 'content' field
    content = forms.CharField(widget=AceWidget(mode='html', theme='monokai', width='900px', height='500px', fontsize='15px'))

    class Meta:
        model = Post
        fields = '__all__'


class DeleteWithImageMixin:
    """
    Admin mixin to handle deletion of models with associated images.
    """
    def delete_queryset(self, request, queryset):
        """
        Deletes all associated image variants for models before removing them from the database.
        """
        for obj in queryset:
            # Check if the model instance has a featured_image field
            if hasattr(obj, 'featured_image') and obj.featured_image:
                # Delete all image variants
                if hasattr(obj, 'get_image_variants'):
                    for variant in obj.get_image_variants().values():
                        try:
                            if os.path.exists(variant['path']):
                                os.remove(variant['path'])
                                self.message_user(request, f"Deleted image variant: {variant['path']}")
                        except Exception as e:
                            self.message_user(request, f"Error deleting image variant for {obj}: {e}", level="error")

                # Delete the original image
                try:
                    if os.path.exists(obj.featured_image.path):
                        os.remove(obj.featured_image.path)
                        self.message_user(request, f"Deleted original image for: {obj}")
                except Exception as e:
                    self.message_user(request, f"Error deleting original image for {obj}: {e}", level="error")

        # Call the parent method to delete the objects
        super().delete_queryset(request, queryset)

@admin.register(Post)
class PostAdmin(DeleteWithImageMixin,admin.ModelAdmin):
    form = PostForm  # Use the custom form
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 
                   'view_count', 'created_at', 'display_featured_image')
    list_filter = ('status', 'is_featured', 'category', 'author', 'created_at')
    search_fields = ('title', 'content', 'meta_title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'featured_image_preview')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    save_on_top = True
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        (_('Featured Image'), {
            'fields': ('featured_image', 'featured_image_preview'),
        }),
        (_('Categories and Tags'), {
            'fields': ('category', 'tags')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Publication Settings'), {
            'fields': ('status', 'is_featured', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
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
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_at',)
        return self.readonly_fields

    def view_count_display(self, obj):
        return format_html('<b>{}</b>', obj.view_count)
    view_count_display.short_description = _('Views')
    view_count_display.admin_order_field = 'view_count'    
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new post
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'view_count', 'status')
    search_fields = ('title', 'content', 'meta_title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count',)
    save_on_top = True
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'content')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('view_count', 'status'), 
            'classes': ('collapse',)
        }),
    )

