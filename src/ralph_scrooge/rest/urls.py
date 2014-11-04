from django.conf.urls import patterns, url

from ralph_scrooge.rest.menu import SubMenu


urlpatterns = patterns(
    '',
    url(
        r'^submenu/$',
        SubMenu.as_view(),
        name='submenu'
    ),
)
