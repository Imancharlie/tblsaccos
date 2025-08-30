"""
WSGI config for TBL SACCOS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Add your project directory to the sys.path
# Update this path to match your PythonAnywhere setup
path = '/home/yourusername/tblsaccos'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tblsaccos.settings')

# Serve Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
