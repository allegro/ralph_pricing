import os
import sys


DEBUG = False

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_ID = 1
USE_I18N = True
USE_L10N = True
MEDIA_URL = '/u/'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'  # noqa
STATICFILES_DIRS = (
    BASE_DIR + '/media',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

SECRET_KEY = 'change me'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_rq',
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'ralph_scrooge',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_USER_MODEL = 'ralph_scrooge.ScroogeUser'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ralph',
        'USER': 'ralph',
        'PASSWORD': 'ralph',
        'HOST': '',
        'PORT': '',
        'OPTIONS': dict(),
    },
}

TIME_ZONE = 'Europe/Warsaw'

LOGIN_URL = '/login/'
ROOT_URLCONF = 'ralph_scrooge.urls'

RQ_QUEUE_LIST = (
    'reports_pricing', 'scrooge_costs_master', 'scrooge_costs',
    'scrooge_report'
)
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
}
for queue in RQ_QUEUE_LIST:
    RQ_QUEUES[queue] = dict(RQ_QUEUES['default'])


CACHES = dict(
    default=dict(
        BACKEND='django.core.cache.backends.locmem.LocMemCache',
        LOCATION='',
        TIMEOUT=300,
        OPTIONS=dict(),
        KEY_PREFIX='RALPH_',
    ),
    staticfiles=dict(
        BACKEND='django.core.cache.backends.locmem.LocMemCache',
        LOCATION='cached_static_files'
    )
)

USAGE_OWNERS_GROUP_NAME = 'usage-owners'

# -----------------------------------------
# SCROOGE SETTINGS
# -----------------------------------------

# Settings for Ralph3-based plugins
RALPH3_API_TOKEN = ''
RALPH3_API_BASE_URL = ''

# NFSEN (network) plugin default config
SSH_NFSEN_CREDENTIALS = {}
NFSEN_CHANNELS = []
NFSEN_CLASS_ADDRESS = []
NFSEN_FILES_PATH = ''
NFSEN_MIN_VALUE = 0

# Virtual Usages plugin default config
VIRTUAL_SERVICES = {}

# Shares plugin default config
SHARE_SERVICES = {}

# OpenStack
OPENSTACK_CEILOMETER = []
OPENSTACK_SIMPLE_USAGES = []
OPENSTACK_TENANTS_MODELS = []
OPENSTACK_NOVA_INSTANCES = []

OPENSTACK_CINDER_VOLUMES = []
OPENSTACK_CINDER_VOLUMES_DONT_CHARGE_FOR_SIZE = []

# VIP
VIP_TYPES = []

# Database
DATABASE_TYPES = []

# Blade server
RALPH3_BLADE_SERVER_CATEGORY_ID = None

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
RALPH3_COLLECT_PLUGINS_MAPPING = {
    'ralph3_service_environment': ['service', 'environment'],
    'ralph3_profit_center': ['profit_center'],
    'ralph3_data_center': ['warehouse'],
    'ralph3_business_segment': ['business_line'],
    'ralph3_asset_model': ['asset_model'],
    'ralph3_asset': ['asset'],
    'ralph3_cloud_project': ['tenant'],
}

SYNC_SERVICES_ONLY_CALCULATED_IN_SCROOGE = False
UNKNOWN_SERVICES_ENVIRONMENTS = {
    'tenant': {},
    'ralph3_tenant': (None, None),
    'netflow': (None, None),
    'ralph3_asset': (None, None),
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

LOAD_BALANCER_TYPES_MAPPING = {
    'HAPROXY': 'HA Proxy',
}

EDITOR_TRACKABLE_MODEL = AUTH_USER_MODEL

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 100,  # 100 MB
            'backupCount': 10,
            'filename': None,  # to be configured in settings-local.py
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },

    },
    'formatters': {
        'verbose': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': (
                '[%(asctime)08s,%(msecs)03d] %(levelname)-7s [%(processName)s'
                ' %(process)d] %(module)s - %(message)s'),
        },
        'simple': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '[%(asctime)08s] %(levelname)-7s %(message)s',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'ralph_scrooge': {
            'handlers': ['file', 'console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
}

# For sending notifications re: detected anomalies / missing values in uploaded
# usages.
EMAIL_HOST = ''
EMAIL_PORT = None
EMAIL_HOST_USER = r''
EMAIL_HOST_PASSWORD = ''
EMAIL_NOTIFICATIONS_SENDER = ''
EMAIL_USE_TLS = False

# Base URL component for constructing Scrooge's links in outgoing mails.
BASE_MAIL_URL = ''

# Values below should be given in days.
USAGE_TYPE_UPLOAD_FREQ_MARGINS = {
    'daily': 1,
    'weekly': 2,
    'monthly': 3,
}
