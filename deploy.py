#!/usr/bin/env python3
"""
TBL SACCOS Deployment Script
Automates the deployment process for PythonAnywhere
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Error: manage.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if Django is installed
    try:
        import django
        print(f"✅ Django {django.get_version()} is available")
    except ImportError:
        print("❌ Django is not installed. Please install requirements first.")
        sys.exit(1)
    
    print("✅ All prerequisites met")

def collect_static():
    """Collect static files"""
    return run_command("python manage.py collectstatic --noinput", "Collecting static files")

def run_migrations():
    """Run database migrations"""
    return run_command("python manage.py migrate", "Running database migrations")

def check_django():
    """Check Django configuration"""
    return run_command("python manage.py check", "Checking Django configuration")

def create_backup():
    """Create a backup of the current database"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = subprocess.run("date +%Y%m%d_%H%M%S", shell=True, capture_output=True, text=True).stdout.strip()
    backup_file = backup_dir / f"backup_{timestamp}.json"
    
    print(f"💾 Creating backup: {backup_file}")
    return run_command(f"python manage.py dumpdata > {backup_file}", "Creating database backup")

def main():
    """Main deployment function"""
    print("🚀 TBL SACCOS Deployment Script")
    print("=" * 50)
    
    # Check prerequisites
    check_prerequisites()
    
    # Create backup
    create_backup()
    
    # Check Django configuration
    if not check_django():
        print("❌ Django check failed. Please fix the issues before deploying.")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("❌ Migrations failed. Please check the database connection.")
        sys.exit(1)
    
    # Collect static files
    if not collect_static():
        print("❌ Static file collection failed.")
        sys.exit(1)
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Upload your project to PythonAnywhere")
    print("2. Configure the WSGI file with your username")
    print("3. Set up static files in PythonAnywhere")
    print("4. Reload your web app")
    print("\n📖 See PYTHONANYWHERE_DEPLOYMENT.md for detailed instructions")

if __name__ == "__main__":
    main()
