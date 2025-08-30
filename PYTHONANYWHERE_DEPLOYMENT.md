# PythonAnywhere Deployment Guide for TBL SACCOS

This guide will walk you through deploying the TBL SACCOS Loan Management System on PythonAnywhere.

## 🚀 Prerequisites

- PythonAnywhere account (free or paid)
- GitHub repository with your project
- Basic knowledge of command line operations

## 📋 Step-by-Step Deployment

### 1. Prepare Your Local Project

First, ensure your project is ready for deployment:

```bash
# Check for any syntax errors
python manage.py check

# Test the application locally
python manage.py runserver

# Create a requirements.txt if you don't have one
pip freeze > requirements.txt
```

### 2. Push to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit for PythonAnywhere deployment"

# Add remote origin
git remote add origin https://github.com/Imancharlie/tblsaccos.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. PythonAnywhere Setup

#### 3.1 Create a New Web App

1. Log in to [PythonAnywhere](https://www.pythonanywhere.com/)
2. Go to the **Web** tab
3. Click **Add a new web app**
4. Choose **Manual configuration** (not Django)
5. Select **Python 3.9** or higher
6. Note your domain: `yourusername.pythonanywhere.com`

#### 3.2 Clone Your Repository

1. Go to the **Consoles** tab
2. Start a new **Bash console**
3. Clone your repository:

```bash
cd ~
git clone https://github.com/Imancharlie/tblsaccos.git
cd tblsaccos
```

#### 3.3 Set Up Virtual Environment

```bash
# Create virtual environment
python3.9 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Configure Django Settings

#### 4.1 Update Production Settings

1. Copy the production settings:

```bash
cp tblsaccos/production.py tblsaccos/settings.py
```

2. Edit the settings file to update your domain:

```python
# Update these lines in tblsaccos/settings.py
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',  # Replace with your actual domain
    'www.yourusername.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Update database path
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'tblsaccos_production.db',
    }
}
```

#### 4.2 Set Environment Variables

Create a `.env` file in your project root:

```bash
nano .env
```

Add the following content:

```env
SECRET_KEY=your-super-secret-key-here
DEBUG=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Configure Web App

#### 5.1 Update WSGI Configuration

1. Go back to the **Web** tab
2. Click on your web app
3. Click **Edit WSGI configuration file**
4. Replace the content with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/tblsaccos'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'tblsaccos.settings'

# Serve Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Important**: Replace `yourusername` with your actual PythonAnywhere username.

#### 5.2 Configure Source Code and Working Directory

1. In the **Web** tab, set:
   - **Source code**: `/home/yourusername/tblsaccos`
   - **Working directory**: `/home/yourusername/tblsaccos`

### 6. Database and Static Files

#### 6.1 Run Migrations

In your Bash console:

```bash
cd ~/tblsaccos
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

#### 6.2 Configure Static Files

1. In the **Web** tab, go to **Static files**
2. Add:
   - **URL**: `/static/`
   - **Directory**: `/home/yourusername/tblsaccos/staticfiles`

3. Add media files:
   - **URL**: `/media/`
   - **Directory**: `/home/yourusername/tblsaccos/media`

### 7. Final Configuration

#### 7.1 Reload Web App

1. Go to the **Web** tab
2. Click **Reload** button
3. Wait for the reload to complete

#### 7.2 Test Your Application

1. Visit `https://yourusername.pythonanywhere.com`
2. Test the login functionality
3. Check if all features are working

### 8. Troubleshooting

#### 8.1 Common Issues

**Error: ModuleNotFoundError**
- Ensure your virtual environment is activated
- Check that all requirements are installed
- Verify the WSGI configuration path

**Error: Database connection issues**
- Check database file permissions
- Ensure database file exists
- Verify database path in settings

**Error: Static files not loading**
- Check static files configuration
- Ensure `collectstatic` was run
- Verify static files directory exists

#### 8.2 Check Logs

1. Go to the **Web** tab
2. Click **Log files**
3. Check **Error log** for detailed error messages

### 9. Security Considerations

#### 9.1 Update Secret Key

Generate a new secret key:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Update your `.env` file with the new key.

#### 9.2 HTTPS Configuration

1. In the **Web** tab, enable **HTTPS**
2. Update your settings to use HTTPS:

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 10. Maintenance

#### 10.1 Regular Updates

```bash
# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install new requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Reload web app
```

#### 10.2 Backup

Regularly backup your database:

```bash
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
```

## 🔧 Advanced Configuration

### Custom Domain

1. Purchase a domain
2. Configure DNS to point to PythonAnywhere
3. Update `ALLOWED_HOSTS` in settings
4. Configure SSL certificate

### Database Optimization

For better performance, consider:
- Using PostgreSQL instead of SQLite
- Implementing database connection pooling
- Adding database indexes

### Performance Monitoring

Monitor your application:
- Check PythonAnywhere usage statistics
- Monitor response times
- Track memory usage

## 📞 Support

If you encounter issues:

1. Check PythonAnywhere documentation
2. Review Django deployment documentation
3. Check the error logs in PythonAnywhere
4. Contact PythonAnywhere support

## 🎉 Success!

Once deployed, your TBL SACCOS application will be accessible at:
`https://yourusername.pythonanywhere.com`

Remember to:
- Keep your secret key secure
- Regularly update dependencies
- Monitor application performance
- Backup your data regularly

---

**Happy Deploying! 🚀**
