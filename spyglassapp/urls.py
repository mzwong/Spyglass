from django.conf.urls import url
from . import views
from django.contrib.staticfiles.urls import static
from django.conf import settings

urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^select_city/$', views.select_city, name='select_city'),
	url(r'^venue_list/$', views.new_york_city_venues, name='new_york_city_venues'),
    url(r'^(?P<city>(new_york|boston))/options/$', views.city_options, name='city_options'),
    url(r'^(?P<city>(new_york|boston))/route/$', views.route, name='route'),
	url(r'^tester/$', views.tester, name='tester'),
]
