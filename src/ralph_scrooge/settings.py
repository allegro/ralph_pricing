# NFSEN (network) plugin default config
SSH_NFSEN_CREDENTIALS = {}
NFSEN_CHANNELS = []
NFSEN_CLASS_ADDRESS = []
NFSEN_FILES_PATH = ''

# Virtual Usages plugin default config
VIRTUAL_VENTURE_NAMES = {}

# Cloud (from Ralph) plugin default config
# CLOUD_UNKNOWN_VENTURE = None

# Shares plugin default config
SHARE_VENTURE_SYMBOLS = {}
# SHARES_UNKNOWN_VENTURES = {}  # symbols

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
    'ceilometer': None,
}
