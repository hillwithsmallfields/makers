# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('/new', views.new_event, name='newevent'),
    path('/<id>', views.one_event, name='oneevent'),
    path('/signup/<id>', views.signup_event, name="signup"),
    path('/complete/<id>', views.complete_event, name='done_event'),
    path('/results', views.store_event_results, name='results'),
    path('/special/<uuid:what>:<uuid:who>:<uuid:admin_user>:<role>:<enable>:<duration>', views.special_event, name='special'),
    path('', views.public_index, name='index')
]
