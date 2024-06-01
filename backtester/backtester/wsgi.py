"""
WSGI config for backtester project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backtester.settings')

# application = get_wsgi_application()



import os

from django.core.wsgi import get_wsgi_application


from pathlib import Path
import dotenv

if os.environ.get('DJANGO_ENV'):
    BASE_DIR = Path(__file__).resolve().parent.parent
    print(f"base dir {BASE_DIR}")
    DOT_ENV_FILE = os.path.join(BASE_DIR , f"{os.environ.get('DJANGO_ENV')}.env")
    if os.path.exists(DOT_ENV_FILE):
        dotenv.load_dotenv(str(DOT_ENV_FILE))
    else:
        print("Dot env file not found")
        exit(1)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    print(f"base dir {BASE_DIR}")
    DOT_ENV_FILE = os.path.join(BASE_DIR , "dev.env")
    if os.path.exists(DOT_ENV_FILE):
        dotenv.load_dotenv(str(DOT_ENV_FILE))
    else:
        print("Dot env file not found")
        exit(1)
    # print("DJANGO_ENV not set in environment")
    # exit(1)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backtester.settings')

application = get_wsgi_application()

