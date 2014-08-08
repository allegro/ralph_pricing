# NFSEN (network) plugin default config
SSH_NFSEN_CREDENTIALS = {}
NFSEN_CHANNELS = []
NFSEN_CLASS_ADDRESS = []
NFSEN_FILES_PATH = ''

# Virtual Usages plugin default config
VIRTUAL_VENTURE_NAMES = {}

# Shares plugin default config
SHARE_SERVICE_CI_UID = {}

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
    'extra_cost',
    'owner',
    'service',
    'warehouse',
])

UNKNOWN_SERVICES_ENVIRONMENTS = {
    'tenant': (None, None),
}
