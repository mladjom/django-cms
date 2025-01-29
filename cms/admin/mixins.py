import os

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