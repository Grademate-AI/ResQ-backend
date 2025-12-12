"""
WSGI config for Grademate project.
"""
import os
import environ

from django.core.wsgi import get_wsgi_application



env = environ.Env()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    env.str("DJANGO_SETTINGS_MODULE", "config.settings.dev")
)

application = get_wsgi_application()

