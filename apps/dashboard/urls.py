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
    # individual sections for loading into tabs
    path('profile', views.profile_only, name='profile_only'),
    path('notifications', views.notifications_only, name='notifications_only'),
    path('responsibilities', views.responsibilities_only, name='responsibilities_only'),
    path('trained_on', views.trained_on_only, name='trained_on_only'),
    path('other_equipment', views.other_equipment_only, name='other_equipment_only'),
    path('hosting', views.events_hosting_only, name='events_hosting_only'),
    path('attending', views.events_attending_only, name='events_attending_only'),
    path('hosted', views.events_hosted_only, name='events_hosted_only'),
    path('attended', views.events_attended_only, name='events_attended_only'),
    path('available', views.events_available_only, name='events_available_only'),
    path('usage_log', views.usage_log_only, name='usage_log_only'),
    path('send_pw_reset', views.send_password_reset, name='send_pw_reset'),
    path('debug_on', views.debug_on, name='debug_on'),
    path('debug_off', views.debug_off, name='debug_off'),
    path('admin_view_as_user_on', views.admin_view_as_user_on, name='admin_view_as_user_on'),
    path('admin_view_as_user_off', views.admin_view_as_user_off, name='admin_view_as_user_off'),
    path('admin', views.admin_only, name='admin_only'),
    path('match', views.user_match_page, name='matching_users'),
    # general default paths etc
    path('<who>', views.dashboard_page, name='user_dashboard'),
    path('', views.dashboard_page, name='own_dashboard')
]
