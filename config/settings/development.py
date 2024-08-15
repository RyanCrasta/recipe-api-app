from .base import *


DEBUG = True
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGIN = ['https://recipe-api-app-production.up.railway.app']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
