# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    path('create_event', views.create_event, name='create_event'),
    path('create_event_2', views.create_event_2, name='create_event_2'),
    path('create_event_template', views.create_event_template, name='create_event_template'),
    path('edit_event_template', views.edit_event_template, name='edit_event_template'),
    path('announce', views.announce, name='announce'),
    path('notify', views.notify, name='notify'),
    path('add_user', views.add_user, name='add_user'),
    path('GDPR_delete_user', views.gdpr_delete_user, name='gdpr_delete_user'),
    path('update_django', views.update_django, name='update_django')
]
