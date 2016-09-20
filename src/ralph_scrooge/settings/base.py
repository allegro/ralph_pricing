import os
import sys


DEBUG = False
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

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

TEMPLATE_DIRS = (BASE_DIR + "templates",)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'tastypie',
    'django_rq',
    'south',
    'rest_framework',
    'ralph_scrooge'
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

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
    'reports_pricing', 'scrooge_costs_master', 'scrooge_costs', 'scrooge_repor'
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

AUTH_PROFILE_MODULE = 'ralph_scrooge.UserProfile'


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

EDITOR_TRACKABLE_MODEL = AUTH_PROFILE_MODULE

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
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
            'datefmt': '%d.%m.%Y %H:%M:%S',
            'format': (
                '[%(asctime)08s,%(msecs)03d] %(levelname)-7s [%(processName)s'
                ' %(process)d] %(module)s - %(message)s'),
        },
        'simple': {
            'datefmt': '%H:%M:%S',
            'format': '[%(asctime)08s] %(levelname)-7s %(message)s',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'plugins': {
            'handlers': ['file', 'console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'ralph_scrooge.management.commands.scrooge_sync': {
            'handlers': ['file', 'console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'critical_only': {
            'handlers': ['file', 'mail_admins'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    },
}
