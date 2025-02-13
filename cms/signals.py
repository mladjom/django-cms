from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import Truncator
from .models import Post
import asyncio
from services import GPT2Service

gpt2_service = GPT2Service()

@receiver(pre_save, sender=Post)
def generate_meta_description(sender, instance, **kwargs):
    """Generate meta description if none exists"""
    if not instance.meta_description and instance.content:
        # Create prompt from first 200 characters of content
        prompt = f"Summarize this text in one sentence: {instance.content[:200]}"
        
        # Generate meta description
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        meta_description = loop.run_until_complete(
            gpt2_service.generate_text(prompt, max_length=160)
        )
        loop.close()
        
        if meta_description:
            instance.meta_description = meta_description


# @receiver(pre_save, sender=Article)
# def set_excerpt(sender, instance, **kwargs):
#     if not instance.excerpt:
#         instance.excerpt = Truncator(instance.content).chars(120, truncate='...')

# @receiver(post_save, sender=Post)
# def update_search_index(sender, instance, **kwargs):
#     # Automatically update search index when an article is saved
#     instance.update_search_index()
