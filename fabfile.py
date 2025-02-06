from fabric import Connection, task, Config
from invoke import run as local
from decouple import config

# from fabric import Connection, task

# # Server configuration (can also be loaded from .env)
# SERVER_HOST = "neotec.blog"
# SERVER_USER = "mladjo"
# PROJECT_ROOT = "/var/www/neotec"
# VENV_PATH = "/home/mladjo/.virtualenv/neotec/bin/activate"
# REPO_URL = "https://github.com/mladjom/django-cms.git"

# @task
# def deploy(c):
#     """Deploy the Django application."""
#     # Step 1: Connect to the server
#     conn = Connection(host=SERVER_HOST, user=SERVER_USER)

#     # Step 2: Pull the latest code from the repository
#     with conn.cd(PROJECT_ROOT):
#         print("Pulling the latest code from the repository...")
#         conn.run("git pull origin main")

#     # Step 3: Install dependencies
#     print("Installing dependencies...")
#     conn.run(f". {VENV_PATH} && pip install -r {PROJECT_ROOT}/requirements.txt")

#     # Step 4: Apply database migrations
#     print("Applying database migrations...")
#     conn.run(f". {VENV_PATH} && python {PROJECT_ROOT}/manage.py migrate")

#     # Step 5: Collect static files
#     print("Collecting static files...")
#     conn.run(f". {VENV_PATH} && python {PROJECT_ROOT}/manage.py collectstatic --noinput")

#     # Step 6: Restart the web server
#     print("Restarting Gunicorn service...")
#     conn.sudo("systemctl restart gunicorn")

#     print("Restarting Nginx service...")
#     conn.sudo("systemctl restart nginx")

#     print("Deployment complete!")




# Server configuration
host = config('SERVER_HOST')
user = config('SERVER_USER')
project_root = config('PROJECT_ROOT')
repo_url = config('REPO_URL')
branch = config('BRANCH', default='main')
venv_path = config('VENV_PATH')
sudo_password = config('SUDO_PASSWORD')

# Set up Fabric connection with sudo password
config_data = Config(overrides={'sudo': {'password': sudo_password}})
conn = Connection(f"{user}@{host}")

@task
def install_system_packages(c):
    """Install required system packages."""
    conn.sudo('apt-get update')
    conn.sudo('apt-get install -y python3-pip python3-venv git')

@task
def create_virtualenv(c):
    """Create virtual environment if it doesn't exist."""
    result = conn.run(f'test -d {venv_path}', warn=True)
    if result.failed:
        conn.run(f'python3 -m venv {venv_path}')

@task
def deploy(c):
    """Main deployment task."""
    result = conn.run(f'test -d {project_root}', warn=True)
    if result.failed:
        # Clone the repository if it doesn't exist
        conn.run(f'git clone {repo_url} {project_root}')
    
    with conn.cd(project_root):
        # Pull latest changes
        conn.run(f'git fetch origin {branch}')
        conn.run(f'git reset --hard origin/{branch}')
        
        # Activate virtualenv and install requirements
        with conn.prefix(f'source {venv_path}/bin/activate'):
            conn.run('pip install -r requirements.txt')
            conn.run('python manage.py collectstatic --noinput')
            conn.run('python manage.py migrate')
            conn.run('python manage.py clear_cache')

@task
def restart_services(c):
    """Restart web server and related services."""
    conn.sudo('systemctl restart gunicorn', password=sudo_password)
    conn.sudo('systemctl restart nginx', password=sudo_password)

@task
def full_deploy(c):
    """Run complete deployment process."""
    install_system_packages(c)
    create_virtualenv(c)
    deploy(c)
    restart_services(c)

@task
def quick_deploy(c):
    """Quick deployment without system updates."""
    deploy(c)
    restart_services(c)

@task
def backup_database(c):
    """Create a database backup."""
    timestamp = conn.run('date +%Y%m%d_%H%M%S').stdout.strip()
    backup_dir = config('BACKUP_DIR', default=f'{project_root}/backups')
    
    result = conn.run(f'test -d {backup_dir}', warn=True)
    if result.failed:
        conn.run(f'mkdir -p {backup_dir}')
    
    with conn.cd(project_root):
        with conn.prefix(f'source {venv_path}/bin/activate'):
            conn.run(f'python manage.py dumpdata --indent 2 > {backup_dir}/backup_{timestamp}.json')

@task
def rollback(c, commit_hash):
    """Rollback to a specific commit."""
    with conn.cd(project_root):
        conn.run(f'git reset --hard {commit_hash}')
        
        with conn.prefix(f'source {venv_path}/bin/activate'):
            conn.run('pip install -r requirements.txt')
            conn.run('python manage.py migrate')
            
    restart_services(c)