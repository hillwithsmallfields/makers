# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    path('create_event', views.create_event, name='create_event'),
    path('create_event_2', views.create_event_2, name='create_event_2'),
    path('edit_event_template', views.edit_event_template, name='edit_event_template'),
    path('save_template_edits', views.save_template_edits, name='save_template_edits'),
    path('announce', views.announce, name='announce'),
    path('notify', views.notify, name='notify'),
    path('send_email', views.send_email, name='send_email'),
    path('add_user', views.add_user, name='add_user'),
    path('backup_database', views.backup_database, name='backup_database'),
    path('update_database', views.update_database, name='update_database'),
    path('raw_database', views.raw_database, name='raw_database'),
    path('GDPR_delete_user', views.gdpr_delete_user, name='gdpr_delete_user'),
    path('test_message', views.test_message, name='test_message'),
    path('update_django', views.update_django, name='update_django')
]
