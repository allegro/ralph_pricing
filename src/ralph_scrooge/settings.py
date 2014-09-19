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
OPENSTACK_TENANT_SERVICE_FIELD = None
OPENSTACK_TENANT_ENVIRONMENT_FIELD = None

# Pricing statistics default config
WARNINGS_LIMIT_FOR_USAGES = 40

# Default collect plugins to run
COLLECT_PLUGINS = set([
    'asset',
    'business_line',
    'environment',
    'owner',
    'service',
    'warehouse',
])

UNKNOWN_SERVICES_ENVIRONMENTS = {
    'tenant': (None, None),
    'netflow': (None, None),
}

ADDITIONAL_PRICING_OBJECT_TYPES = {}

import sys
TESTING = 'test' in sys.argv
