from django import template
from django.utils.safestring import mark_safe
from cms.settings import IMAGE_SETTINGS

register = template.Library()

@register.simple_tag
def responsive_image(image_field, alt_text="",  css_class="", sizes=None):
    """
    Generates a responsive <img> tag with srcset for the given ImageField.

    :param image_field: The ImageField instance (e.g., `post.featured_image`)
    :param alt_text: Alt text for the image (default: empty string)
    :param sizes: A list of sizes for the srcset (default: IMAGE_SETTINGS['SIZES'])
    :param css_class: CSS class for the <img> tag (default: empty string)
    :return: HTML <img> tag
    usage : {% responsive_image post.featured_image alt_text=post.title css_class="rounded-lg shadow-lg" %}
    """
    # Ensure image_field is provided
    if not image_field:
        return ""

    # Validate that the object has a URL
    if not hasattr(image_field, 'url'):
        raise ValueError("The provided image_field does not have a valid URL.")

    sizes = IMAGE_SETTINGS['SIZES']
    base_url, ext = str(image_field.url).rsplit('.', 1)

    # Generate srcset
    srcset = [
        f"{base_url}.webp {size}w" for size in sizes
    ]
    srcset_str = ", ".join(srcset)

    # Largest size for fallback
    largest_size = max(sizes)
    fallback_url = f"{base_url}-{largest_size}w.webp"

    # Responsive image tag
    img_tag = (
        f'<img src="{fallback_url}" alt="{alt_text}" class="{css_class}" '
        f'srcset="{srcset_str}" sizes="100vw" loading="lazy" decoding="async">'
    )
    return mark_safe(img_tag)