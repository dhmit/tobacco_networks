"""
Rereading URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URL configuration
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url

from apps.common import render_react_view
from apps.main import views as main_views


urlpatterns = [
    # Django admin page
    path('admin/', admin.site.urls),

    # API endpoints
    # might want to change name later
    url('api/edges/', main_views.list_edges),
    # temporary json endpoint for network data
    url('get_network_data', main_views.get_network_data),

    # React views
    url('', render_react_view, {'component_name': 'MainView'}),

    # Person_info views
    url('api/person_info/', main_views.get_person_info),
]
