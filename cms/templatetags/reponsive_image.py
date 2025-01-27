from django import template
from django.utils.safestring import mark_safe
from cms.settings import IMAGE_SETTINGS

register = template.Library()

@register.simple_tag
def responsive_image(post, sizes=None):
    """
    Render responsive image markup
    
    usage: {% responsive_image post %}
    """
    if not post.featured_image:
        return ''
    
    sizes = sizes or IMAGE_SETTINGS['SIZES']
    versions = post.featured_image_versions or {}
    
    # Construct srcset
    srcset = []
    for size in sizes:
        version = next((v for k, v in versions.items() if int(k.split('x')[0]) == size), None)
        if version:
            srcset.append(f"{version['path']} {version['width']}w")
    
    # Fallback image (typically medium size)
    fallback_size = sizes[len(sizes) // 2]
    fallback_version = next((v for k, v in versions.items() if int(k.split('x')[0]) == fallback_size), None)
    
    if not fallback_version:
        return ''
    
    # Construct HTML
    return mark_safe(f'''
        <img 
            src="{fallback_version['path']}"
            srcset="{', '.join(srcset)}"
            sizes="(max-width: 1200px) 100vw, 1200px"
            alt="{post.title}"
            loading="lazy"
        />
    ''')