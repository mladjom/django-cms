from fabric import Connection, task
import os
from datetime import datetime

# Configuration (now loaded from .env)
DEPLOY_USER = os.getenv('DEPLOY_USER', 'user')
DEPLOY_HOST = os.getenv('DEPLOY_HOST', 'site.com')
PROJECT_PATH = os.getenv('PROJECT_PATH', '/var/www/project_folder')
VENV_PATH = os.getenv('VENV_PATH', '/home/mladjo/.virtualenvs/venv_folder')
REPO_URL = os.getenv('REPO_URL', 'https://github.com/yourusername/project.git')

def get_connection():
    return Connection(
        host=DEPLOY_HOST,
        user=DEPLOY_USER,
        connect_kwargs={
            "key_filename": "~/.ssh/id_rsa",
        }
    )

@task
def deploy_from_github(ctx):
    """Deploy by pulling directly from GitHub"""
    conn = get_connection()
    
    with conn.cd(PROJECT_PATH):
        # Pull latest changes
        conn.run('git pull origin main')
        
        # Update dependencies and migrate
        with conn.prefix(f'source {VENV_PATH}/bin/activate'):
            conn.run('pip install -r requirements.txt')
            conn.run('python manage.py migrate')
            conn.run('python manage.py collectstatic --noinput')
        
        # Restart Gunicorn
        conn.sudo('systemctl restart gunicorn')

@task
def first_time_setup(ctx):
    """Setup the server for the first time"""
    conn = get_connection()
    
    # Create project directory
    conn.sudo(f'mkdir -p {PROJECT_PATH}')
    conn.sudo(f'chown {DEPLOY_USER}:{DEPLOY_USER} {PROJECT_PATH}')
    
    # Clone the repository
    with conn.cd('/var/www'):
        conn.run(f'git clone {REPO_URL} neotec')
    
    # Create and setup virtualenv
    conn.run(f'python -m venv {VENV_PATH}')
    
    with conn.prefix(f'source {VENV_PATH}/bin/activate'):
        conn.run('pip install -r requirements.txt')
        conn.run('python manage.py migrate')
        conn.run('python manage.py collectstatic --noinput')

@task
def sync_media(ctx):
    """Sync media files from local to server"""
    conn = get_connection()
    
    # Create backup of server media
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    conn.run(f'cp -r {PROJECT_PATH}/media {PROJECT_PATH}/media_backup_{timestamp}')
    
    # Sync media files
    os.system(f'rsync -avz media/ {DEPLOY_USER}@{DEPLOY_HOST}:{PROJECT_PATH}/media/')
