# encoding=utf8
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'chiffee/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^home/$', views.showoverview, name='home'),
    url(r'^money/$', views.showmoney, name='money'),
    url(r'^prod/$', views.showproducts, name='prod'),
    url(r'^history/$', views.showhistory, name='history'),
    url(r'^timeout/$', views.timeout, name='timeout'),
    url(r'^balance/$', views.balance, name='balance'),
    
    
    url(r'^$', views.users, name='index'),
    url(r'^(?P<userID>[0-9,a-z,A-Z,\s]+)/$', views.products, name='products'),
    url(r'^(?P<userID>[0-9,a-z,A-Z,\s]+)/(?P<productID>[0-9,a-z,A-Z,\-,\.,\,\s]+)/$', views.confirm, name='confirm'),
    url(r'^(?P<userID>[0-9,a-z,A-Z,\s]+)/(?P<productID>[0-9,a-z,A-Z,\-,\.,\,\s]+)/(?P<count>[0-9]+)$', views.confirmed, name='confirmed'),

]
