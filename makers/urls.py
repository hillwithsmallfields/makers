"""makers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.views.generic.base import RedirectView, TemplateView
from django.contrib.auth import views as auth_views

import makers_admin.views
import dashboard.views
import equiptypes.views
import machines.views
import events.views
import training.views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('dashboard/', include('dashboard.urls'), name='dashboard'),
    path('equiptypes/', include('equiptypes.urls'), name='equiptypes'),
    path('machines/', include('machines.urls', namespace='machines'), name='machines'),
    path('makers_admin/', include('makers_admin.urls', namespace='makers_admin'), name='makers_admin'),
    path('events/', include('events.urls'), name='events'),
    path('training/', include('training.urls'), name='training'),
    # path('users/', include('users.urls'), name='users'),
    path('users/', include('django.contrib.auth.urls'), name='users'),

    # re_path(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    # re_path(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    # re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm, name='password_reset_confirm'),
    # re_path(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

    path('', RedirectView.as_view(url='/dashboard/'))

    # path('', TemplateView.as_view(template_name='home.html'), name='home')
]

# from https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website|:
# Use static() to add url mapping to serve static files during development (only)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
