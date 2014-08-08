# NFSEN (network) plugin default config
SSH_NFSEN_CREDENTIALS = {}
NFSEN_CHANNELS = []
NFSEN_CLASS_ADDRESS = []
NFSEN_FILES_PATH = ''

# Virtual Usages plugin default config
VIRTUAL_VENTURE_NAMES = {}

# Shares plugin default config
SHARE_VENTURE_SYMBOLS = {}

# OpenStack
OPENSTACK_TENANT_SERVICE_FIELD = None

# Pricing statistics default config
WARNINGS_LIMIT_FOR_USAGES = 40

# Default collect plugins to run
COLLECT_PLUGINS = set([
    'assets',
    'extra_cost',
    'ventures',
    'virtual',
    'warehouse',
])

UNKNOWN_SERVICES = {
    'tenant': None,
}
