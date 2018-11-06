"""IOTSignals URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))

"""
from django.conf import settings
from django.conf.urls import url, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import routers
from rest_framework import permissions

from passage import views as passage_views


class IOTSignalsView(routers.APIRootView):
    """
    Store IOT Signals.

    These could be notifications or measuremetns or signals from
    any IOT in the city device.
    """


class Router(routers.DefaultRouter):
    APIRootView = IOTSignalsView


router = Router()

router.register('milieuzone/passage', passage_views.PassageViewSet)

urls = router.urls


schema_view = get_schema_view(
    openapi.Info(
        title="IOT Signals Container API",
        default_version='v1',
        description="IOTSignals in Amsterdam",
        terms_of_service="https://data.amsterdam.nl/",
        contact=openapi.Contact(email="datapunt@amsterdam.nl"),
        license=openapi.License(name="CC0 1.0 Universal"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # url(r"^afval/stats/", include(stats.urls)),
    url(r'^iotsignals/swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^iotsignals/swagger/$',
        schema_view.with_ui('swagger', cache_timeout=None),
        name='schema-swagger-ui'),
    url(r'^iotsignals/redoc/$',
        schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    url(r"^iotsignals/", include(urls)),
    # url(r"^status/", include("health.urls")),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])