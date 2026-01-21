"""
WSGI config for sistema project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
if settings_module in ('sistema.sistema.settings', 'sistema.sistema'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema.settings'
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema.settings')

application = get_wsgi_application()
