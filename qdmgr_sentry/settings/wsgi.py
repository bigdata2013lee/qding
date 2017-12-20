# -*- coding: utf-8 -*-
import os,sys

sys.stdout = sys.stderr

os.system('export PYTHONIOENCODING=utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.default')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()