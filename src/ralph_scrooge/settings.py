import sys
from lck.django import current_dir_support

execfile(current_dir_support)

DEBUG = True
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SITE_ID = 1
USE_I18N = True
USE_L10N = True
MEDIA_URL = '/u/'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
STATICFILES_DIRS = (
    CURRENT_DIR + 'media',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'lck.django.common.middleware.ForceLanguageCodeMiddleware',
)

TEMPLATE_DIRS = (CURRENT_DIR + "templates",)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_rq',
    'south',
    'rest_framework',
    'ajax_select',
    'bob',
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
        'OPTIONS': dict(
        ),
    },
}

ROOT_URLCONF = 'ralph_scrooge.urls'

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

RQ_QUEUE_LIST = ('reports_pricing',)
RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 0,
    },
}
for queue in RQ_QUEUE_LIST:
     RQ_QUEUES[queue] = dict(RQ_QUEUES['default'])

SYNC_SERVICES_ONLY_CALCULATED_IN_SCROOGE = False
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
