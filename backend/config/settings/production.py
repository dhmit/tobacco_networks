"""

Local development Django settings for dhmit/tobacco_networks

Under no circumstances run the server with these settings in production!

"""

from .base import *  # pylint: disable=unused-wildcard-import, wildcard-import


# SECURITY WARNING: keep the secret key used in production secret!
# TODO(ra): read from an environment variable!
# TODO(ra): read from an environment variable!
# TODO(ra): read from an environment variable!
# TODO(ra): read from an environment variable!
SECRET_KEY = 'qqucn931x78rx054n(6g(s_3vxppjw$f24e(9&v6rsbd0&0$2e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'tobacconetworks.dhmit.xyz',
    'tobacconetworks.dhlab.mit.edu',
]

CORS_ORIGIN_ALLOW_ALL = True
