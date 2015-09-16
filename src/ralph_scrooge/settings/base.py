# -*- coding: utf-8 -*-
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'CHANGE_ME'

DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'simple_history',
    'rest_framework',
    'rest_framework.authtoken',
    'ralph_scrooge',
    'tastypie',
)

# MIDDLEWARE_CLASSES = (
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
# )

ROOT_URLCONF = 'ralph_scrooge.urls'
URLCONF_MODULES = [ROOT_URLCONF]

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#             'loaders': [
#                 'django.template.loaders.filesystem.Loader',
#                 'django.template.loaders.app_directories.Loader',
#             ]
#         },
#     },
# ]

WSGI_APPLICATION = 'ralph_scrooge.wsgi.application'

MYSQL_OPTIONS = {
    'sql_mode': 'TRADITIONAL',
    'charset': 'utf8',
    'init_command': """
    SET storage_engine=INNODB;
    SET character_set_connection=utf8,collation_connection=utf8_unicode_ci;
    SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
    """
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_ENV_MYSQL_DATABASE', 'scrooge'),
        'USER': os.environ.get('DB_ENV_MYSQL_USER', 'scrooge'),
        'PASSWORD': os.environ.get('DB_ENV_MYSQL_PASSWORD', 'scrooge'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'OPTIONS': MYSQL_OPTIONS,
        'ATOMIC_REQUESTS': True,
    }
}

LANGUAGE_CODE = 'en-us'
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# STATIC_URL = '/static/'
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )
# STATIC_ROOT = os.path.join(BASE_DIR, 'var', 'static')

MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'var', 'media')
# MEDIA_URL = '/u/'
STATIC_URL = '/static/'
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'media'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'lck.django.staticfiles.LegacyAppDirectoriesFinder',
)

DEFAULT_DEPRECIATION_RATE = 25
LDAP_SERVER_OBJECT_USER_CLASS = 'user'  # possible values: user, person
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'ralph_scrooge': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',  # noqa
    'PAGE_SIZE': 10,
}


RQ_QUEUE_LIST = (
    'reports', 'reports_pricing', 'scrooge_report',
    'scrooge_collect', 'scrooge_costs', 'scrooge_costs_master',
)
RQ_QUEUES = {
    'default': {
        'HOST': 'ralph_redis_master',
        'PORT': 6379,
        'DB': 3,
        'PASSWORD': 'ralph666',
    },
}
for queue in RQ_QUEUE_LIST:
    RQ_QUEUES[queue] = dict(RQ_QUEUES['default'])

# NFSEN (network) plugin default config
SSH_NFSEN_CREDENTIALS = {}
NFSEN_CHANNELS = []
NFSEN_CLASS_ADDRESS = []
NFSEN_FILES_PATH = ''

# Virtual Usages plugin default config
VIRTUAL_SERVICES = {}

# Shares plugin default config
SHARE_SERVICES = {}

# OpenStack
OPENSTACK_CEILOMETER = []
OPENSTACK_SIMPLE_USAGES = []
OPENSTACK_TENANTS_MODELS = []
OPENSTACK_NOVA_INSTANCES = []

# VIP
VIP_TYPES = []

# Database
DATABASE_TYPES = []

# Pricing statistics default config
WARNINGS_LIMIT_FOR_USAGES = 40

# Default collect plugins to run
COLLECT_PLUGINS = set([
    'asset_model',
    'asset',
    'database',
    'business_line',
    'environment',
    'owner',
    'profit_center',
    'service',
    'tenant',
    'warehouse',
    'vip',
    'virtual',
])

UNKNOWN_SERVICES_ENVIRONMENTS = {
    'tenant': {},
    'netflow': (None, None),
}

ADDITIONAL_PRICING_OBJECT_TYPES = {}

SAVE_ONLY_FIRST_DEPTH_COSTS = True
DAILY_COST_CREATE_BATCH_SIZE = 10000
SCROOGE_COSTS_MASTER_SLEEP = 1

TESTING = 'test' in sys.argv

PRICING_OBJECTS_COSTS_TABLE_SCHEMA = {
    'Asset': {
        'fields': [
            'id',
            'name',
            'assetinfo.sn',
            'assetinfo.barcode'
        ],
        'model': 'ralph_scrooge.models.AssetInfo',
    },
    'Virtual': {
        'fields': [
            'id',
            'name',
            'model.name',
        ],
        'model': 'ralph_scrooge.models.VirtualInfo',
    },
    'IP Address': {
        'fields': [
            'id',
            'name'
        ],
    },
    'OpenStack Tenant': {
        'fields': [
            'id',
            'name',
            'tenantinfo.tenant_id',
            'model.name',
        ],
        'model': 'ralph_scrooge.models.TenantInfo',
    },
    'VIP': {
        'fields': [
            'id',
            'name',
            'model.name',
        ],
        'model': 'ralph_scrooge.models.VIPInfo',
    },
    'Database': {
        'fields': [
            'id',
            'name',
            'model.name',
        ],
        'model': 'ralph_scrooge.models.DatabaseInfo',
    },
}

COMPONENTS_TABLE_SCHEMA = {
    'Asset': {
        'fields': [
            'pricing_object.id',
            'pricing_object.name',
            'pricing_object.assetinfo.sn',
            'pricing_object.assetinfo.barcode'
        ],
        'model': 'ralph_scrooge.models.DailyAssetInfo',
    },
    'Virtual': {
        'fields': [
            'pricing_object.id',
            'pricing_object.name',
            'pricing_object.model.name',
            ('dailyvirtualinfo.hypervisor.pricing_object.name', 'Hypervisor'),
        ],
        'model': 'ralph_scrooge.models.DailyVirtualInfo',
    },
    'IP Address': {
        'fields': [
            'pricing_object.id',
            'pricing_object.name'
        ],
    },
    'OpenStack Tenant': {
        'fields': [
            'pricing_object.id',
            'pricing_object.name',
            'pricing_object.tenantinfo.tenant_id',
            'pricing_object.model.name',
        ],
        'model': 'ralph_scrooge.models.DailyTenantInfo',
    },
    'VIP': {
        'fields': [
            'pricing_object.id',
            'pricing_object.name',
            'pricing_object.model.name',
        ],
        'model': 'ralph_scrooge.models.DailyVIPInfo',
    },
    'Database': {
        'fields': [
            'pricing_object.id',
            'pricing_object.name',
            'pricing_object.model.name',
        ],
        'model': 'ralph_scrooge.models.DailyDatabaseInfo',
    },
}
