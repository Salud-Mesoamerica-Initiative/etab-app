
from .common import *
env = environ.Env(DEBUG=(bool, False),)
environ.Env.read_env(ROOT_DIR('.env'))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    }
}

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = ['*']

# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# AWS_S3_FORCE_HTTP_URL = True
# AWS_QUERYSTRING_AUTH = False
#
# AWS_SECRET_ACCESS_KEY = os.environ.get('ORCHID_AWS_SECRET_ACCESS_KEY')
# AWS_ACCESS_KEY_ID = os.environ.get('ORCHID_AWS_ACCESS_KEY_ID')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('ORCHID_AWS_STORAGE_BUCKET_NAME')

CELERYCONF = {
    'CELERY_ALWAYS_EAGER': True,
    'BROKER_URL': 'amqp://guest:guest@localhost:5672//'
}
