# My Awesome Site

A modern and minimal website built with Django and Tailwind CSS.

## Features

- **Django Backend** – A powerful and scalable backend.
- **Tailwind CSS** – A sleek and responsive frontend design.
- **SEO Optimized** – Meta tags, breadcrumbs, and structured data.
- **Contact Form** – Secure email handling with admin notifications.
- **Blog System** – Categories, tags, and featured images with responsive handling.

## Installation

### Prerequisites

- Python 3.x
- Virtual environment (`venv` recommended)
- PostgreSQL (or any other preferred database)
- Node.js & npm (for Tailwind CSS)

### Setup

1. **Clone the repository:**

   ```sh
   git clone git@github.com:yourusername/yourproject.git
   cd yourproject
   ```

2. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:** Copy `.env.example` to `.env` and configure your settings.

5. **Migrations:**

   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser:**

   ```sh
   python manage.py createsuperuser
   ```

7. **Run the development server:**

   ```sh
   python manage.py runserver
   ```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

---



