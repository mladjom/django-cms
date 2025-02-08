from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from ..models import SiteSettings

register = template.Library()

register = template.Library()

@register.simple_tag
def responsive_image(image_field, alt_text="", css_class="", sizes=None, loading="lazy"):
    """
    Generates a responsive <img> tag with srcset for the given ImageField.
    Supports both WebP and original format fallback.

    Args:
        image_field: The ImageField instance (e.g., `post.featured_image`)
        alt_text: Alt text for the image (default: empty string)
        css_class: CSS class for the <img> tag (default: empty string)
        sizes: Optional list of sizes for the srcset. If None, uses site settings.
        loading: Image loading strategy ("lazy", "eager", or "auto")

    Returns:
        HTML <img> tag wrapped in <picture> for format fallback

    Usage:
        {% responsive_image post.featured_image alt_text=post.title css_class="rounded-lg shadow-lg" %}
    """
    # Handle empty image field
    if not image_field:
        return ""

    # Validate image field
    if not hasattr(image_field, 'url'):
        raise ValueError("The provided image_field does not have a valid URL.")

    try:
        # Get site settings for image sizes
        site_settings = SiteSettings.get_settings()
        sizes = sizes or site_settings.image_sizes

        # Clean and escape input
        alt_text = escape(alt_text)
        css_class = escape(css_class)
        base_url, ext = str(image_field.url).rsplit('.', 1)

        # Generate srcset for WebP
        webp_srcset = [
            f"{base_url}.{ext} {size}w" for size in sizes
        ]
        webp_srcset_str = ", ".join(webp_srcset)

        # Determine sizes attribute
        sizes_attr = "100vw"  # Can be customized based on your needs

        # Create picture element with source and img
        picture_tag = f"""
            <picture>
                <source
                    type="image/webp"
                    srcset="{webp_srcset_str}"
                    sizes="{sizes_attr}">
                <img
                    src="{base_url}-{max(sizes)}w.{ext}"
                    alt="{alt_text}"
                    class="{css_class}"
                    loading="{loading}"
                    decoding="async">
            </picture>
        """.strip()

        return mark_safe(picture_tag)

    except Exception as e:
        # Log the error and return empty string or fallback image
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating responsive image: {str(e)}")
        return ""