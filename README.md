# Django CMS

![Django](https://img.shields.io/badge/Django-5.1.5-green.svg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A modern, lightweight, and high-performance content management system built with Django and Tailwind CSS. This CMS provides a clean, responsive interface focused on speed, SEO, and content management flexibility.

## 🌟 Features

- **Modern Stack**: Built with Django 5.1.5 and Tailwind CSS for a powerful backend and sleek frontend
- **Responsive Design**: Fully responsive layout that looks great on all devices
- **Advanced SEO Tools**:
  - Meta title and description management
  - Automatic sitemap generation
  - JSON-LD structured data for enhanced search engine visibility
  - SEO-friendly URLs and breadcrumbs
- **Content Management**:
  - Rich text editor with syntax highlighting using Ace
  - Categories and tags for content organization
  - Featured images with automatic resizing and WebP conversion
  - Scheduled publishing
- **Performance Optimized**:
  - Responsive image handling with WebP support
  - Database query optimization
  - Cache-friendly architecture
- **Content Features**:
  - Blog system with categories, tags, and featured posts
  - Reading time estimation
  - View counters
  - Related posts
- **RSS/Atom Feeds**: Automatic feed generation for blogs and categories
- **Contact Form**: Secure email handling with admin notifications
- **Internationalization**: Multi-language support via Django's i18n
- **Admin Interface**: Enhanced Django admin with custom actions and previews

## 📋 Requirements

- Python 3.12+
- PostgreSQL (recommended) or SQLite
- Node.js and npm (for Tailwind CSS)

## 🚀 Installation

### Step 1: Clone the repository

```bash
git clone git@github.com:mladjom/django-cms.git
cd django-cms
```

### Step 2: Set up Python environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Configure environment variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your specific settings
nano .env
```

Required environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to True for development, False for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_ENGINE`: Database engine (default: django.db.backends.sqlite3)
- `DB_NAME`: Database name
- `DB_USER`: Database user (if using PostgreSQL)
- `DB_PASSWORD`: Database password (if using PostgreSQL)
- `DB_HOST`: Database host (if using PostgreSQL)
- `DB_PORT`: Database port (if using PostgreSQL)

### Step 4: Set up the database

```bash
python manage.py migrate
```

### Step 5: Create a superuser

```bash
python manage.py createsuperuser
```

### Step 6: Compile Tailwind CSS

```bash
cd theme
npm install
npm run dev  # For development with auto-reloading
# or
npm run prod  # For production
```

### Step 7: Run the development server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to see your site in action.

## 📝 Usage

### Content Management

1. Log in to the admin panel at http://127.0.0.1:8000/admin/
2. Create categories and tags
3. Create and publish your posts and pages
4. Customize site settings

### Site Customization

- **Themes**: Modify Tailwind CSS in the `theme` directory
- **Templates**: Customize templates in the `templates` directory
- **Static Files**: Add custom JS, CSS, and images in the `static` directory

## 📚 Development

### Running Tests

```bash
python manage.py test
```

### Creating Sample Data

```bash
python manage.py seed_database
```

### Fabric Deployment

For deployment, this project includes Fabric scripts:

```bash
# Full deployment
fab full_deploy

# Quick deployment (without system updates)
fab quick_deploy

# Database backup
fab backup_database
```

## 🔧 Key Files and Directories

- `cms/`: Core application folder
- `config/`: Project configuration and settings
- `static/`: Static files (CSS, JS, images)
- `templates/`: HTML templates
- `theme/`: Tailwind CSS configuration and source
- `media/`: User-uploaded files (created at runtime)

## 📊 Data Model

The CMS consists of several key models:

- **Post**: Blog posts with rich content and metadata
- **Page**: Static pages
- **Category**: Post categories with hierarchical support
- **Tag**: Post tags for granular organization
- **SiteSettings**: Global site configuration
- **ContactMessage**: Stored contact form submissions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [ACE Editor](https://ace.c9.io/)

---

Made with ❤️ by [Your Name]