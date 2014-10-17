from django.conf.urls import patterns, url

from ralph_scrooge.rest.menu import Menu


urlpatterns = patterns(
    '',
    url(
        r'^menu/$',
        Menu.as_view(),
        name='menu'
    ),
)
