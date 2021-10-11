# Application version (Major, minor, patch)
from typing import Literal

VERSION = (0, 0, 1)

# API versions (Major, minor, patch)
API_VERSIONS = {
    'v0': (0, 0, 2),
    # 'v1': (1, 1, 0),
    'v2': (2, 0, 0),
}

# This can be a little confusing since the api version number (i.e. the one
# used in the URL) for version 1 of the payload is 0, from version 2 the version
# numbers are the same. In other words...
#
#    payload version  |  api version
#    --------------------------------
#    passage-v1       |  v0
#    passage-v2       |  v2
#
PayloadVersion = Literal['passage-v1', 'passage-v2']
ApiVersion = Literal['v0', 'v2']


def to_api_version(payload_version: PayloadVersion) -> ApiVersion:
    return {'passage-v1': 'v0', 'passage-v2': 'v2'}[payload_version]
