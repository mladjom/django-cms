from fabric import Connection, task, Config
from invoke import run as local
from decouple import config
import logging
import os
import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def log_command(command, result):
    """Helper function to log command execution"""
    logger.info(f"Executing: {command}")
    if result.failed:
        logger.error(f"Failed with exit code {result.exited}")
        logger.error(f"Stderr: {result.stderr}")
    else:
        logger.info(f"Success! Exit code: {result.exited}")
        if result.stdout:
            logger.debug(f"Output: {result.stdout}")

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
def setup_env_file(c):
    """Copy and rename .env.production to .env on the server"""
    logger.info("Setting up environment file...")
    
    with conn.cd(project_root):
        # Check if .env already exists
        result = conn.run('test -f .env', warn=True)
        if not result.failed:
            # Backup existing .env if it exists
            timestamp = conn.run('date +%Y%m%d_%H%M%S').stdout.strip()
            logger.info("Backing up existing .env file")
            conn.run(f'cp .env .env.backup_{timestamp}')
        
        # Check if .env.production exists
        result = conn.run('test -f .env.production', warn=True)
        if result.failed:
            logger.error(".env.production file not found!")
            return False
        
        # Copy .env.production to .env
        logger.info("Copying .env.production to .env")
        result = conn.run('cp .env.production .env')
        log_command('cp .env.production .env', result)
        
        # Set proper permissions
        conn.run('chmod 600 .env')
        logger.info("Environment file setup completed")
        return True
    
@task
def copy_production_env(c, local_path='.env.production'):
    """Copy local .env.production file to server"""
    logger.info(f"Copying {local_path} to server...")
    
    if not os.path.exists(local_path):
        logger.error(f"Local file {local_path} not found!")
        return False
    
    # Create temporary directory if it doesn't exist
    conn.run('mkdir -p /tmp/env_transfer')
    
    try:
        # Upload the file
        result = conn.put(local_path, '/tmp/env_transfer/.env.production')
        log_command('put .env.production', result)
        
        # Move it to project directory
        with conn.cd(project_root):
            conn.run('mv /tmp/env_transfer/.env.production .')
            conn.run('chmod 600 .env.production')
        
        logger.info("Environment file transfer completed")
        return True
    
    finally:
        # Cleanup
        conn.run('rm -rf /tmp/env_transfer')
        
def ensure_directory_permissions(conn, path):
    """Ensure proper permissions on directory and contents"""
    with conn.sudo():
        conn.run(f'chown -R {conn.user}:www-data {path}')
        conn.run(f'chmod -R g+w {path}')
            
@task
def deploy(c):
    """Main deployment task with enhanced logging"""
    logger.info("Starting deployment process...")
    
    result = conn.run(f'test -d {project_root}', warn=True)
    if result.failed:
        logger.info("Project directory not found, cloning repository...")
        result = conn.run(f'git clone {repo_url} {project_root}')
        log_command('git clone', result)
    
    with conn.cd(project_root):
        logger.info("Pulling latest changes...")
        result = conn.run(f'git fetch origin {branch}')
        log_command('git fetch', result)
        
        result = conn.run(f'git reset --hard origin/{branch}')
        log_command('git reset', result)
        
        with conn.prefix(f'source {venv_path}/bin/activate'):
            logger.info("Installing dependencies...")
            result = conn.run('pip install -r requirements.txt')
            log_command('pip install', result)
            
            logger.info("Collecting static files...")
            result = conn.run('python manage.py collectstatic --noinput')
            log_command('collectstatic', result)
            
            logger.info("Running migrations...")
            result = conn.run('python manage.py migrate')
            log_command('migrate', result)
            
            logger.info("Clearing cache...")
            result = conn.run('python manage.py clear_cache')
            log_command('clear_cache', result)

@task
def restart_services(c):
    """Restart web server and related services."""
    conn.sudo('systemctl restart gunicorn', password=sudo_password)
    conn.sudo('systemctl restart nginx', password=sudo_password)
    
@task
def quick_deploy(c):
    """Quick deployment without system updates."""
    deploy(c)
    restart_services(c)
    
@task
def full_deploy(c):
    """Complete deployment process with environment setup"""
    install_system_packages(c)
    create_virtualenv(c)
    copy_production_env(c)
    setup_env_file(c)
    deploy(c)
    restart_services(c)

@task
def backup_database(c):
    """Create a database backup."""
    logger.info("Starting database backup...")
    
    # Get timestamp for backup file
    timestamp = conn.run('date +%Y%m%d_%H%M%S').stdout.strip()
    
    # Use backup directory from config with fallback
    backup_dir = config('BACKUP_DIR', default='/db_backups')
    
    # Create backup directory if it doesn't exist
    result = conn.run(f'test -d {backup_dir}', warn=True)
    if result.failed:
        logger.info(f"Creating backup directory: {backup_dir}")
        try:
            conn.sudo(f'mkdir -p {backup_dir}', password=sudo_password)
            conn.sudo(f'chown {user}:{user} {backup_dir}', password=sudo_password)
            conn.sudo(f'chmod 755 {backup_dir}', password=sudo_password)
        except Exception as e:
            logger.error(f"Failed to create backup directory: {e}")
            raise
    
    # Define file paths
    temp_backup = f'{project_root}/backup_temp_{timestamp}.json'
    final_backup = f'{backup_dir}/backup_{timestamp}.json'
    
    logger.info(f"Creating backup at: {final_backup}")
    
    try:
        # Create the backup file in the project directory
        with conn.cd(project_root):
            with conn.prefix(f'source {venv_path}/bin/activate'):
                result = conn.run(f'python manage.py dumpdata --indent 2 > {temp_backup}')
                log_command('dumpdata', result)
        
        # Now copy the file to the backup directory using sudo
        conn.sudo(f'cp {temp_backup} {final_backup}', password=sudo_password)
        conn.sudo(f'chown {user}:{user} {final_backup}', password=sudo_password)
        conn.sudo(f'chmod 644 {final_backup}', password=sudo_password)
        
        # Remove the temporary file
        conn.run(f'rm -f {temp_backup}')
        
        logger.info(f"Backup completed successfully: {final_backup}")
        
        # Clean up old backups (keeping last 5)
        cleanup_cmd = f"find {backup_dir} -name 'backup_*.json' -type f -printf '%T@ %p\\n' | sort -n | head -n -5 | cut -d' ' -f2- | xargs -r rm"
        conn.sudo(cleanup_cmd, password=sudo_password, warn=True)
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        # Clean up temp file if it exists
        conn.run(f'rm -f {temp_backup}', warn=True)
        raise

@task
def rollback(c, commit_hash):
    """Rollback to a specific commit."""
    with conn.cd(project_root):
        conn.run(f'git reset --hard {commit_hash}')
        
        with conn.prefix(f'source {venv_path}/bin/activate'):
            conn.run('pip install -r requirements.txt')
            conn.run('python manage.py migrate')
            
    restart_services(c)

@task
def sync_db_to_local(c):
    """Import production database to local environment"""
    logger.info("Starting database sync to local...")
    
    # Get database credentials from local .env
    db_name = config('DB_NAME')
    db_user = config('DB_USER')
    db_password = config('DB_PASSWORD')
    
    # Create temp directory
    timestamp = local('date +%Y%m%d_%H%M%S', hide=True).stdout.strip()
    temp_dir = f'/tmp/db_sync_{timestamp}'
    local(f'mkdir -p {temp_dir}')
    
    try:
        # Create remote backup - Using sudo to become postgres user first
        dump_file = f'db_dump_{timestamp}.sql'
        dump_command = f'cd {project_root} && pg_dump {db_name}'
        
        # Execute pg_dump as postgres user
        conn.sudo(f'su - postgres -c "{dump_command}" > {project_root}/{dump_file}',
                 password=sudo_password)
        
        # Ensure the dump file is readable
        conn.sudo(f'chmod 644 {project_root}/{dump_file}', password=sudo_password)
        
        # Download backup
        conn.get(f'{project_root}/{dump_file}', f'{temp_dir}/{dump_file}')
        
        # Drop and recreate local database
        local(f'dropdb {db_name}', warn=True)
        local(f'createdb {db_name}')
        
        # Import backup
        local(f'psql -U {db_user} -d {db_name} -f {temp_dir}/{dump_file}')
        
        logger.info("Database sync completed successfully")
        
    except Exception as e:
        logger.error(f"Database sync failed: {e}")
        raise
        
    finally:
        # Cleanup
        conn.sudo(f'rm -f {project_root}/{dump_file}', password=sudo_password, warn=True)
        local(f'rm -rf {temp_dir}')

@task 
def sync_media_to_local(c):
    """Download media files from production"""
    logger.info("Starting media sync to local...")
    
    # Get media paths
    remote_media = f"{project_root}/media/"
    local_media = "media/"
    
    # Create local media directory if it doesn't exist
    local('mkdir -p media')
    
    try:
        # Create temporary archive on server
        with conn.cd(project_root):
            archive_name = "media_archive.tar.gz"
            conn.run(f'tar -czf {archive_name} media/')
        
        # Download archive
        conn.get(f'{project_root}/{archive_name}', archive_name)
        
        # Extract locally
        local(f'tar -xzf {archive_name}')
        
        logger.info("Media sync completed successfully")
        
    except Exception as e:
        logger.error(f"Media sync failed: {e}")
        raise
        
    finally:
        # Cleanup
        with conn.cd(project_root):
            conn.run(f'rm -f {archive_name}', warn=True)
        local(f'rm -f {archive_name}')

@task
def sync_all_to_local(c):
    """Sync both database and media files to local"""
    sync_db_to_local(c)
    sync_media_to_local(c)
    
@task
def sync_db_to_prod(c, force=False):
    """Push local database to production"""
    if not force and not input("⚠️ This will overwrite production database. Type 'yes' to confirm: ") == 'yes':
        return
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_dir = f'/tmp/db_sync_{timestamp}'
    local(f'mkdir -p {temp_dir}')
    dump_file = f'local_db_dump_{timestamp}.sql'
    
    try:
        # Backup production first
        backup_database(c)
        
        # Dump local database
        local(f'pg_dump -U {config("DB_USER")} {config("DB_NAME")} > {temp_dir}/{dump_file}')
        
        # Upload dump
        conn.put(f'{temp_dir}/{dump_file}', f'{project_root}/{dump_file}')
        
        # Import on production
        with conn.cd(project_root):
            conn.sudo(f'psql -U postgres {config("DB_NAME")} < {dump_file}', password=sudo_password)
            
    finally:
        local(f'rm -rf {temp_dir}')
        with conn.cd(project_root):
            conn.run(f'rm -f {dump_file}', warn=True)

@task
def sync_media_to_prod(c, force=False):
    """Push local media files to production"""
    if not force and not input("⚠️ This will overwrite production media. Type 'yes' to confirm: ") == 'yes':
        return
    
    archive_name = "local_media_archive.tar.gz"
    
    try:
        # Archive local media
        local('tar -czf local_media_archive.tar.gz media/')
        
        # Upload and extract
        conn.put(archive_name, f'{project_root}/{archive_name}')
        with conn.cd(project_root):
            conn.run(f'tar -xzf {archive_name}')
            conn.sudo(f'chown -R {user}:www-data media/', password=sudo_password)
            conn.sudo(f'chmod -R g+w media/', password=sudo_password)
            
    finally:
        local(f'rm -f {archive_name}')
        with conn.cd(project_root):
            conn.run(f'rm -f {archive_name}')

@task
def sync_all_to_prod(c, force=False):
    """Push both database and media to production"""
    sync_db_to_prod(c, force)
    sync_media_to_prod(c, force)