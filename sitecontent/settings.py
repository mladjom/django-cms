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

    # Category-specific settings
    'TAXONOMY': {
        'WIDTH': 768,
        'ASPECT_RATIO': (16, 10)
    }
}

SITE = {
    'NAME': 'Site Name',
    'DESCRIPTION': 'Site Description',
    'URL': 'https://www.example.com',
    'EMAIL': '.'.join(['info', 'example', 'com']),
}