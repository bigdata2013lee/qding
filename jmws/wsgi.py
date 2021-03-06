# -*- coding: utf-8 -*-

"""
This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys
from django.core.wsgi import get_wsgi_application

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(base_path)

# Portable WSGI applications should not write to sys.stdout or use the 'print' statement
# without specifying an alternate file object besides sys.stdout as the target'
sys.stdout = sys.stderr
os.system('export PYTHONIOENCODING=utf-8')

SETTINGS = 'web.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS)

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.

application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)


