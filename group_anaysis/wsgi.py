import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'group_anaysis.settings')

application = get_wsgi_application()
