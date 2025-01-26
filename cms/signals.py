from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import Truncator
from .models import Post

# @receiver(pre_save, sender=Article)
# def set_excerpt(sender, instance, **kwargs):
#     if not instance.excerpt:
#         instance.excerpt = Truncator(instance.content).chars(120, truncate='...')

# @receiver(post_save, sender=Post)
# def update_search_index(sender, instance, **kwargs):
#     # Automatically update search index when an article is saved
#     instance.update_search_index()
