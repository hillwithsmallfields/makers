# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('new', views.new_event, name='new_event'),
    path('search', views.search_events, name='search_events'),
    path('signup', views.signup_event, name="signup"),
    path('rsvp_form/<id>', views.rsvp_event_form, name="rsvp_form"),
    path('rsvp', views.rsvp_event, name="rsvp"),
    path('complete/<id>', views.complete_event, name='done_event'),
    path('results', views.store_event_results, name='results'),
    path('special', views.special_event, name='special'),
    path('<id>', views.one_event, name='oneevent'),
    path('', views.public_index, name='index')
]
