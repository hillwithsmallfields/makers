# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_page, name='own_dashboard'),
    path('<who>', views.dashboard_page, name='user_dashboard'),
    path('all', views.user_list_page, name='all_users'),
    path('match/<pattern>', views.user_match_page, name='matching_users')
]
