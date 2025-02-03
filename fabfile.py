from fabric import Connection, task
import os

# Get deployment settings from environment variables
DEPLOY_USER = os.getenv('DEPLOY_USER', 'user')
DEPLOY_HOST = os.getenv('DEPLOY_HOST', 'site.com')
PROJECT_PATH = '/var/www/neotec'
VENV_PATH = '/home/mladjo/.virtualenvs/neotec'

def get_connection():
    return Connection(
        host=DEPLOY_HOST,
        user=DEPLOY_USER,
        connect_kwargs={
            "key_filename": "~/.ssh/id_rsa",
        }
    )

def deploy():
    conn = get_connection()
    
    # Pull latest changes
    with conn.cd(PROJECT_PATH):
        conn.run('git pull origin main')
    
    # Update dependencies
    with conn.prefix(f'source {VENV_PATH}/bin/activate'):
        with conn.cd(PROJECT_PATH):
            conn.run('pip install -r requirements.txt')
    
    # Run migrations
    with conn.prefix(f'source {VENV_PATH}/bin/activate'):
        with conn.cd(PROJECT_PATH):
            conn.run('python manage.py migrate')
            conn.run('python manage.py collectstatic --noinput')
    
    # Restart Gunicorn
    conn.sudo('systemctl restart gunicorn')

if __name__ == "__main__":
    deploy()