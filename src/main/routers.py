"""Router configuration for multiple versions"""

from django.urls import reverse
from rest_framework import routers

from main import API_VERSIONS
from main.version import get_version


class IOTSignalsAPIRootView(routers.APIRootView):
    """
    List IOT Signals API's and their related information.

    These API endpoints are part of the
    IOT Signalen Informatievoorziening Amsterdam

    The code for this application (and associated web front-end)
    is available from:

    - https://github.com/Amsterdam/iotsignals

    Note:
    Most of these endpoints (will) require some form of authentication.
    """

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # Appending the index view with API version 0 information.
        response.data = {
            f'v{version}': {
                '_links': {
                    'self': {
                        'href': request._request.build_absolute_uri(
                            reverse(f'v{version}:api-root')),
                    }
                },
                'version': get_version(API_VERSIONS[f'v{version}']),
                'status': 'in development',
            }
            for version in [0, 2]
        }
        return response

    def get_view_name(self):
        return 'IOT Signals API'


class IOTSignalsAPIVersion0(routers.APIRootView):
    """Signalen API versie 0 (in development)."""

    def get_view_name(self):
        return 'Signals API Version 0'


class IOTSignalsAPIVersion2(routers.APIRootView):
    """Signalen API versie 2 (in development)."""

    def get_view_name(self):
        return 'Signals API Version 2'


class IOTSignalsRouterRoot(routers.DefaultRouter):
    APIRootView = IOTSignalsAPIRootView


class IOTSignalsRouterVersion0(routers.DefaultRouter):
    APIRootView = IOTSignalsAPIVersion0


class IOTSignalsRouterVersion2(routers.DefaultRouter):
    APIRootView = IOTSignalsAPIVersion2

