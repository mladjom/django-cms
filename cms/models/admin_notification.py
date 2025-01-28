from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class AdminNotification(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    message = models.TextField(verbose_name=_("Message"))
    level = models.CharField(max_length=20, choices=[
        ('info', _('Information')),
        ('warning', _('Warning')),
        ('error', _('Error'))
    ], verbose_name=_("Level"))
    recipients = models.ManyToManyField(User, related_name='admin_notifications', verbose_name=_("Recipients"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expires At"))
    is_read = models.BooleanField(default=False, verbose_name=_("Is Read"))

    class Meta:
        verbose_name = _("Admin Notification")
        verbose_name_plural = _("Admin Notifications")
        ordering = ['-created_at']

    def __str__(self):
        return self.title