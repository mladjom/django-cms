from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ..models import SiteSettings

class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'blog_title')
    fieldsets = (
        (_('Site Settings'), {
            'fields': ('site_name', 'site_description', 'site_tagline'),
        }),
        (_('Blog Settings'), {
            'fields': ('blog_title', 'blog_description', 'blog_tagline', 
                       'blog_category_title', 'blog_category_description', 'blog_category_tagline'),
        }),
        (_('Image Settings'), {
            'fields': (
                'image_sizes',
                'image_webp_quality',
                ('image_aspect_ratio_width', 'image_aspect_ratio_height'),
                'image_upload_path_format'
            ),
            'description': _('Configure image processing and storage settings')
        }),
        (_('Google Analytics Settings'), {
            'fields': ('google_analytics_id',),
        }),
    )
    readonly_fields = ('id',) 
    save_on_top = True
    
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """
        Disable delete permission.
        """
        return False

    # def save_model(self, request, obj, form, change):
    #     """
    #     Ensure only one instance exists.
    #     """
    #     if obj.pk is None:
    #         try:
    #             existing_obj = self.model.objects.get(pk=1)
    #             obj.pk = existing_obj.pk
    #         except self.model.DoesNotExist:
    #             pass
    #     super().save_model(request, obj, form, change)