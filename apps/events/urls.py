# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('/new', views.new_event, name='newevent')
    path('', views.public_index, name='index')
]
