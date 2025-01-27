SITE_SETTINGS = {
    'NAME': 'Your Brand Name',  # Replace with your actual brand name
    'DESCRIPTION': 'A platform for engaging content and valuable insights.',
    'TAGLINE': 'Empowering you with knowledge and inspiration.',  # Clear value proposition
    'URL': 'https://www.your-website.com',  # Replace with your actual domain
    'LOGO': '/static/images/logo.png',  # Update path if your logo is elsewhere
}

BLOG_SETTINGS = {
    'TITLE': 'Your Blog Name',  # Replace with your blog's specific name
    'DESCRIPTION': 'Dive deeper into industry trends, explore practical tips, and discover inspiring stories.',
    'TAGLINE': 'Insights to elevate your knowledge and fuel your success.',  # Focus on reader benefits
    'CATEGORY': {
        'TITLE': 'Explore by Category',
        'DESCRIPTION': 'Discover content tailored to your interests.',
        'TAGLINE': 'Find what resonates with you.',  # Highlight category browsing value
    },
}
# Image Processing Settings
IMAGE_SETTINGS = {
    # Default image sizes for responsive images
    'SIZES': [576, 768, 992, 1200],
    
    # Image quality settings
    'WEBP_QUALITY': 85,
    
    # Default aspect ratio (16:10)
    'ASPECT_RATIO': (16, 9),
    
    # Upload path settings
    'UPLOAD_PATH_FORMAT': '{model_name}s/{year}/{month}/{day}',

    # Taxonomy-specific settings
    'TAXONOMY': {
        'WIDTH': 768,
        'ASPECT_RATIO': (16, 10)
    }
}