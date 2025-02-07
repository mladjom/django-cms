from decouple import config

IMAGE_SETTINGS = {
    'SIZES': [576, 768, 992, 1200],
    'WEBP_QUALITY': 85,
    'ASPECT_RATIO': (16, 9),
    'UPLOAD_PATH_FORMAT': '{model_name}s/{year}/{month}/{day}',
    'TAXONOMY': {
        'WIDTH': 768,
        'ASPECT_RATIO': (16, 10)
    }
}