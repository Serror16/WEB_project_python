from pathlib import Path
from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parent.parent

include(
    "components/apps.py",
    "components/databases.py",
    "components/internationalization.py",
    "components/middlewares.py",
    "components/security.py",
    "components/templates.py",
    "components/validators.py",
)

ALLOWED_HOSTS = []

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework_xml.parsers.XMLParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

STATIC_URL = 'static/'
