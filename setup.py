#!/usr/bin/env python3
"""
TBL SACCOS Loan Management System Setup Script
This script helps you set up the system quickly.
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def create_virtual_environment():
    """Create a virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def activate_virtual_environment():
    """Activate the virtual environment"""
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_script = "venv/bin/activate"
    
    if os.path.exists(activate_script):
        print("✅ Virtual environment created successfully")
        print("   To activate it, run:")
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        return True
    else:
        print("❌ Virtual environment activation script not found")
        return False

def install_dependencies():
    """Install required packages"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def setup_database():
    """Set up the database"""
    commands = [
        ("python manage.py makemigrations", "Creating database migrations"),
        ("python manage.py migrate", "Applying database migrations"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def copy_logo():
    """Copy the logo to the static directory"""
    source = "tblsaccos_logo.png"
    destination = "static/tblsaccos_logo.png"
    
    if os.path.exists(source):
        if not os.path.exists("static"):
            os.makedirs("static")
        
        try:
            shutil.copy2(source, destination)
            print("✅ Logo copied to static directory")
            return True
        except Exception as e:
            print(f"❌ Failed to copy logo: {e}")
            return False
    else:
        print("⚠️  Logo file not found in root directory")
        print("   Please ensure tblsaccos_logo.png exists")
        return False

def create_superuser():
    """Create a superuser account"""
    print("🔄 Creating superuser account...")
    print("   Please follow the prompts to create your admin account")
    
    try:
        subprocess.run("python manage.py createsuperuser", shell=True, check=True)
        print("✅ Superuser created successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Superuser creation was cancelled or failed")
        print("   You can create one later with: python manage.py createsuperuser")
        return True

def main():
    """Main setup function"""
    print("🚀 TBL SACCOS Loan Management System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Setup failed at virtual environment creation")
        sys.exit(1)
    
    # Activate virtual environment
    if not activate_virtual_environment():
        print("❌ Setup failed at virtual environment activation")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Copy logo
    if not copy_logo():
        print("⚠️  Logo copy failed, but continuing with setup")
    
    # Set up database
    if not setup_database():
        print("❌ Setup failed at database setup")
        sys.exit(1)
    
    # Create superuser
    if not create_superuser():
        print("❌ Setup failed at superuser creation")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Run the development server:")
    print("   python manage.py runserver")
    print("3. Open your browser and go to: http://127.0.0.1:8000/")
    print("4. Login with your superuser credentials")
    print("\n📚 For more information, see README.md")
    print("\n🌟 Welcome to TBL SACCOS Loan Management System!")

if __name__ == "__main__":
    main()

