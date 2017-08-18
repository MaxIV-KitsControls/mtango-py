from utils import Version


# Base URL
app_base = "/tango/rest"

# Server version
version = Version([0, 1, 2, "alpha"])

# No of worker processes
workers = 4

# Sanic debug mode
debug = True

# Host to bind
host = "0.0.0.0"

# Server port
port = 8000

# rc3 API mode, can be one of these:
# 	strict = follow the documentation
# 	implementation = follow existing mTango rc3 implementation
# The strict mode doesn't disable endpoints not supported in original mTango
rc3_mode = "strict"

# Proxy cache size (if set to None, cache grows indefinitely and nothing is removed)
cache_size = 64
