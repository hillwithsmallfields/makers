# based on https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/skeleton_website etc

from django.urls import path, re_path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('all', views.all_user_list_page, name='all_users'),
    path('update_mugshot', views.update_mugshot, name='update_mugshot'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('update_configured_profile', views.update_configured_profile, name='update_configured_profile'),
    path('update_site_controls', views.update_site_controls, name='update_site_controls'),
    path('update_availability', views.update_availability, name='update_availability'),
    path('update_levels', views.update_levels, name='update_levels'),
    path('update_avoidances', views.update_avoidances, name='update_avoidances'),
    path('announcements_read', views.announcements_read, name='announcements_read'),
    path('notifications_read', views.notifications_read, name='notifications_read'),
    path('reset_messages', views.reset_messages, name='reset_messages'),
    path('<who>', views.dashboard_page, name='user_dashboard'),
    path('match/<pattern>', views.user_match_page, name='matching_users'),
    re_path('match?pattern=.+', views.user_match_page, name='matching_users'), # todo: fix this
    path('', views.dashboard_page, name='own_dashboard')
]
