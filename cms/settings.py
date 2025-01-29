from decouple import config

# Site Structure Settings
SITE_SETTINGS = {
    'NAME': config('SITE_NAME', default='Your Brand Name'),
    'DESCRIPTION': config('SITE_DESCRIPTION', default='A platform for engaging content and valuable insights.'),
    'TAGLINE': config('SITE_TAGLINE', default='Empowering you with knowledge and inspiration.'),
    'URL': config('SITE_URL', default='https://www.your-website.com'),
    'LOGO': config('SITE_LOGO', default='/static/images/logo.png'),
}

BLOG_SETTINGS = {
    'TITLE': config('BLOG_TITLE', default='Your Blog Name'),
    'DESCRIPTION': config('BLOG_DESCRIPTION', default='A collection of articles to inspire and inform.'),
    'TAGLINE': config('BLOG_TAGLINE', default='Explore the latest insights and ideas.'),
    'CATEGORY': {
        'TITLE': config('BLOG_CATEGORY_TITLE', default='Explore by Category'),
        'DESCRIPTION': config('BLOG_CATEGORY_DESCRIPTION', default='Browse articles by topic to find the information you need.'),
        'TAGLINE': config('BLOG_CATEGORY_TAGLINE', default='Discover articles tailored to your interests.'),
    },
}

# These are more like constants than configuration
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