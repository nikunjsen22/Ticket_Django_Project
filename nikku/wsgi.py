"""
WSGI config for nikku project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
project_home = os.path.expanduser('~/nikku')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nikku.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "nikku.settings"
os.environ["RENDER"] = "true"

# Create the WSGI application
application = get_wsgi_application()
