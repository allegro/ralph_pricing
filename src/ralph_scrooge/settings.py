import sys

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
