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

# Pricing statistics default config
WARNINGS_LIMIT_FOR_USAGES = 40

# Default collect plugins to run
COLLECT_PLUGINS = set([
    'asset',
    'business_line',
    'environment',
    'owner',
    'profit_center',
    'service',
    'warehouse',
])

UNKNOWN_SERVICES_ENVIRONMENTS = {
    'tenant': {},
    'netflow': (None, None),
}

ADDITIONAL_PRICING_OBJECT_TYPES = {}

import sys
TESTING = 'test' in sys.argv

COMPONENTS_TABLE_SCHEMA = {
    'Asset': {
        'fields': ['id', 'name', 'assetinfo.sn', 'assetinfo.barcode'],
        'model': 'ralph_scrooge.models.DailyAssetInfo',
    },
    'Virtual': {
        'fields': ['id', 'name', 'virtualinfo.device_id'],
        'model': 'ralph_scrooge.models.DailyVirtualInfo',
    },
    'IP Address': {
        'fields': ['id', 'name'],
    },
    'OpenStack Tenant': {
        'fields': [
            'id',
            'name',
            'tenantinfo.tenant_id',
            'tenantinfo.device_id',
        ],
        'model': 'ralph_scrooge.models.DailyTenantInfo',
    }
}
