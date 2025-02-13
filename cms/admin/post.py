from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from .mixins import DeleteWithImageMixin
from .forms import PostForm

class PostAdmin(DeleteWithImageMixin, admin.ModelAdmin):
    form = PostForm
    list_display = (
        'title', 'author', 'category', 'status', 
        'is_featured', 'view_count', 'created_at', 
        'display_featured_image'
    )
    list_filter = ('status', 'is_featured', 'category', 'author', 'created_at')
    search_fields = ('title', 'content', 'meta_title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'featured_image_preview')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    actions = ('make_draft', 'make_review', 'make_published', 'make_featured', 'make_not_featured')
    save_on_top = True
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt', 'summary')
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
    
    # Custom actions for status
    @admin.action(description=_("Mark selected posts as Draft"))
    def make_draft(modeladmin, request, queryset):
        queryset.update(status='draft')

    @admin.action(description=_("Mark selected posts as Under Review"))
    def make_review(modeladmin, request, queryset):
        queryset.update(status='review')

    @admin.action(description=_("Mark selected posts as Published"))
    def make_published(modeladmin, request, queryset):
        queryset.update(status='published')

    # Custom actions for is_featured
    @admin.action(description=_("Mark selected posts as Featured"))
    def make_featured(modeladmin, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description=_("Mark selected posts as Not Featured"))
    def make_not_featured(modeladmin, request, queryset):
        queryset.update(is_featured=False)

    
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