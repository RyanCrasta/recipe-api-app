from .base import *


DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'recipe-api-app-production.up.railway.app']

CSRF_TRUSTED_ORIGIN = ['https://recipe-api-app-production.up.railway.app']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
