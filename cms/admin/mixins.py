import os
from django.urls import path
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from ..services import GPT2Service
import asyncio
from django.http import JsonResponse, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
        
class GPT2AdminMixin:
    """Mixin to add GPT-2 text generation capabilities to admin classes"""
    
    def get_urls(self):
        # Get info about the model for URL naming
        info = self.model._meta.app_label, self.model._meta.model_name
        
        urls = super().get_urls()
        custom_urls = [
            path('generate-text/', 
                 self.admin_site.admin_view(self.generate_text_view),
                 name='%s_%s_generate' % info),
        ]
        return custom_urls + urls

    def generate_text_view(self, request):
        """
        View to handle text generation requests.
        Requires staff privileges and valid CSRF token.
        """
        if not request.user.is_staff:
            return JsonResponse({'error': 'Staff privileges required'}, status=403)
            
        if request.method != 'POST':
            return JsonResponse({'error': 'Only POST requests allowed'}, status=405)
            
        prompt = request.POST.get('prompt')
        field = request.POST.get('field')
        
        if not prompt or not field:
            return JsonResponse({
                'error': 'Missing required parameters'
            }, status=400)
            
        try:
            # Set max length based on field type
            field_max_lengths = {
                'meta_description': 160,
                'meta_title': 60,
                'description': 500
            }
            max_length = field_max_lengths.get(field, 100)
            
            # Run async text generation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            gpt2_service = self.get_gpt2_service()
            
            try:
                generated_text = loop.run_until_complete(
                    gpt2_service.generate_text(
                        prompt=prompt,
                        max_length=max_length
                    )
                )
                
                if generated_text is None:
                    return JsonResponse({
                        'error': 'Text generation failed'
                    }, status=500)
                    
                return JsonResponse({'text': generated_text})
                
            finally:
                loop.close()
                
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    def get_gpt2_service(self):
        """Get GPT2 service instance - can be overridden if needed"""
        from ..services import GPT2Service
        return GPT2Service()

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