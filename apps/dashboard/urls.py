# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('all', views.all_user_list_page, name='all_users'),
    path('update_mugshot', views.update_mugshot, name='update_mugshot'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('<who>', views.dashboard_page, name='user_dashboard'),
    path('match/<pattern>', views.user_match_page, name='matching_users'),
    path('', views.dashboard_page, name='own_dashboard')
]
