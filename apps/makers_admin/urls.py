# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    path('create_event', views.create_event, name='create_event'),
    path('create_event_2', views.create_event_2, name='create_event_2'),
    path('announce', views.announce, name='announce'),
    path('notify', views.notify, name='notify'),
    path('adduser', views.add_user, name='add_user'),
    path('update_django', views.update_django, 'update_django')
]
