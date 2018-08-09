# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    path('create_event', views.create_event, name='create_event'),
]
