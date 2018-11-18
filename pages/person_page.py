from django.conf import settings
from untemplate.throw_out_your_templates_p3 import htmltags as T
import bson
import datetime
import django.middleware.csrf
import django.urls
import model.configuration
import model.equipment_type
import model.event
import model.pages
import model.person
import model.timeline
import model.timeslots
import pages.event_page
import pages.page_pieces
import pages.user_list_page
import pprint
import untemplate.throw_out_your_templates_p3 as untemplate

all_conf = None
server_conf = None
org_conf = None

def visibility_radio(label, visibility):
    """Make a set of radio buttons for user visibility."""
    return ["No", (T.input(type='radio',
                           name=label,
                           value='no',
                           checked='checked')
                   if visibility == False
                   else T.input(type='radio',
                                name=label,
                                value='no')),
            "Logged in users only", (T.input(type='radio',
                                             name=label,
                                             value='logged_in',
                                             checked='checked')
                                     if visibility == 'logged_in'
                                     else T.input(type='radio',
                                                  name=label,
                                                  value='logged_in')),
            "Yes", (T.input(type='radio',
                           name=label,
                           value='yes',
                           checked='checked')
                   if visibility == True
                   else T.input(type='radio',
                                name=label,
                                value='yes'))]

def site_controls_sub_section(who, viewer, django_request):
    return T.div(class_="site_options")[
        [T.form(action=django.urls.reverse("dashboard:update_site_controls"), method='POST')
         [T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
          T.input(type="hidden",
                  name="subject_user_uuid",
                  value=model.pages.bare_string_id(who._id)),
          model.pages.with_help(
              viewer,
              T.table(class_="siteoptions")[
                  T.tr[T.th(class_="ralabel")["Visible as host / owner / trainer to attendees / users"],
                       T.td[visibility_radio("visibility_as_host", who.visibility.get('host', True))]],
                  T.tr[T.th(class_="ralabel")["Visible as attendee / user to hosts / owners / trainers"],
                       T.td[visibility_radio("visibility_as_attendee", who.visibility.get('attendee', True))]],
                  T.tr[T.th(class_="ralabel")["Visible generally"],
                       T.td[visibility_radio("visibility_in_general", who.visibility.get('general', False))]],
                  T.tr[T.th(class_="ralabel")["Stylesheet"],
                       T.td[pages.page_pieces.dropdown('stylesheet', model.configuration.get_stylesheets(), who.stylesheet)]],
                  T.tr[T.th(class_="ralabel")["Display help beside forms"],
                       T.td[T.input(type='checkbox', name='display_help', checked='checked')
                            if who.show_help
                            else T.input(type='checkbox', name='display_help')]],
                  T.tr[T.th(class_="ralabel")["Notify training etc by email"],
                       T.td[T.input(type='checkbox', name='notify_by_email', checked='checked')
                            if who.notify_by_email
                            else T.input(type='checkbox', name='notify_by_email')]],
                  T.tr[T.th(class_="ralabel")["Notify training etc in site"],
                       T.td[T.input(type='checkbox', name='notify_in_site', checked='checked')
                            if who.notify_in_site
                            else T.input(type='checkbox', name='notify_in_site')]],
                  T.tr[T.th(class_="ralabel")["Developer mode"],
                       T.td[T.input(type='checkbox', name='developer_mode', checked='checked')
                            if who.developer_mode
                            else T.input(type='checkbox', name='developer_mode')]],
                  T.tr[T.th[""], T.td[T.input(type="submit", value="Update controls")]]],
              "site_controls")]]]

def availability_sub_section(who, viewer, django_request):
    _, timeslot_times, _ = model.timeslots.get_slots_conf()
    return model.pages.with_help(viewer,
                                 pages.page_pieces.availform(who, who.available, django_request),
                                 "availability",
                                 substitutions={'morning_start': str(timeslot_times['Morning'][0]),
                                                'morning_end': str(timeslot_times['Morning'][1]),
                                                'afternoon_start': str(timeslot_times['Afternoon'][0]),
                                                'afternoon_end': str(timeslot_times['Afternoon'][1]),
                                                'evening_start': str(timeslot_times['Evening'][0]),
                                                'evening_end': str(timeslot_times['Evening'][1])})

def user_interests_section(who, django_request):
    return pages.page_pieces.interests_section(who.get_interests(),
                                               who.get_profile_field('interest_emails', [False, False, False, False]),
                                               django_request,
                                               who)

def avoidances_section(who, django_request):
    if 'dietary_avoidances' not in all_conf:
        return []
    avoidances = who.get_profile_field('avoidances') or []
    return [T.form(action=django.urls.reverse("dashboard:update_avoidances"),
                   method='POST')[
                       T.table[
                           T.thead[T.tr[T.th(class_='ralabel')["Food"],
                                        T.th["Status"]]],
                           T.tbody[[T.tr[T.th(class_='ralabel')[thing],
                                         T.td[(T.input(type="checkbox",
                                                       name=thing,
                                                       checked="checked")
                                               if thing in avoidances
                                               else T.input(type="checkbox",
                                                            name=thing))]]
                                    for thing in sorted(all_conf['dietary_avoidances'])]]],
                       T.input(type="hidden",
                               name="csrfmiddlewaretoken",
                               value=django.middleware.csrf.get_token(django_request)),
                       T.input(type='hidden',
                               name='subject_user_uuid',
                               value=model.pages.bare_string_id(who._id)),
                       T.div(align="right")[T.input(type='submit', value="Update avoidances")]]]

def get_profile_subfield_value(who, group_name, name):
    all_groups = who.get_profile_field('configured')
    if all_groups is None:
        return ""
    group = all_groups.get(group_name, {})
    if type(group) != dict:
        return ""
    return group.get(name, "")

def mugshot_section(who, viewer, django_request):
    mugshot_filename = who.get_profile_field('mugshot')
    mugshot_url = (django_request.scheme + "://"
                   + (settings.AWS_STORAGE_BUCKET_NAME
                  if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME')
                             else model.configuration.get_config('server', 'domain')) + "/"
                   + mugshot_filename) if mugshot_filename else None
    return [T.form(action=django.urls.reverse("dashboard:update_mugshot"),
                   enctype="multipart/form-data",
                   method='POST')
            [T.img(src=mugshot_url,
                   align="right",
                   alt="Photo of "+who.name()) if mugshot_url else "Picture would go here",
             "Upload new photo: ", T.input(type="file",
                                           name="mugshot",
                                           accept='image/jpeg'),
             T.input(type="hidden",
                     name="csrfmiddlewaretoken",
                     value=django.middleware.csrf.get_token(django_request)),
             T.input(type="hidden",
                     name="subject_user_uuid",
                     value=model.pages.bare_string_id(who.link_id)),
             T.input(type="submit", value="Update photo")]]

def general_profile_section(who, viewer, django_request):
    membership_number = str(who.membership_number)
    subject_login_name = model.database.person_get_login_name(who) or ""
    logged_in_as = django_request.user.username
    table_contents = [
                T.tr[T.th(class_="ralabel")["Name"],
                     T.td[T.input(type="text",
                                  name="name",
                                  value=who.name())]],
                T.tr[T.th(class_="ralabel")["User login name"],
                     T.td[T.input(type='text',
                                  name='login_name',
                                  value=subject_login_name)]],
                T.tr[T.th(class_="ralabel")["Logged in as"],
                     T.td[T.span(class_=('own_view'
                                         if logged_in_as == subject_login_name
                                         else 'admin_view'))[logged_in_as]]],
                          T.tr[T.th(class_="ralabel")["email"], T.td[T.input(type="email",
                                                                             name="email",
                                                                             value=who.get_email())]],
                T.tr[T.th(class_="ralabel")["Membership number"],
                     T.td[(T.input(type="text",
                                   name='membership_number',
                                   value=membership_number)
                                     if (viewer.is_administrator()
                                         and (membership_number == "" or membership_number == "0"))
                                     else [membership_number])]],
                T.tr[T.th(class_="ralabel")['Fob number'],
                     T.td[(T.input(type="text",
                                   name="fob",
                                   value=str(who.fob))
                                     if viewer.is_administrator()
                                     else [str(who.fob)])]],
                T.tr[T.th(class_="ralabel")["link-id"], T.td[str(who.link_id)]],
                T.tr[T.th(class_="ralabel")["No-shows"], T.td[str(len(who.get_noshows()))]],
                T.tr[T.th(class_="ralabel")["No-show absolutions"],
                     T.td[(T.input(type='text',
                                   name='absolutions',
                                   value=str(who.noshow_absolutions))
                           if viewer.is_administrator()
                           else str(who.noshow_absolutions))]],
                T.tr[T.th(class_="ralabel")['Admin note'],
                     T.td[T.input(type='text',
                                  name='note',
                                   value=str(who.get_admin_note()))
                          if viewer.is_administrator()
                          else str(who.get_admin_note())]],
                T.tr[T.th[""], T.td[T.input(type='submit', value="Update details")]]]
    if who.developer_mode:
        pp = pprint.PrettyPrinter(indent=4, width=72)
        table_contents += [T.tr[T.th(class_="ratoplabel")["Debug information"],
                                T.td(class_="developer_data")[T.pre[pp.pformat(who.__dict__)]]],
                           T.tr[T.th(class_="ratoplabel")["Django session data"],
                                T.td(class_="developer_data")[T.pre[pp.pformat(django_request.session.__dict__)]]],
                           T.tr[T.th(class_="ratoplabel")["Django logged-in user data"],
                                T.td(class_="developer_data")[T.pre[pp.pformat(django_request.user.__dict__)]]],
                           T.tr[T.th(class_="ratoplabel")["Django request data"],
                                T.td(class_="developer_data")[T.pre[pp.pformat(django_request.__dict__)]]]]
    return [model.pages.with_help(
        viewer,
        T.form(action=django.urls.reverse("dashboard:update_profile"), method='POST')[
            T.input(type="hidden",
                    name="csrfmiddlewaretoken",
                    value=django.middleware.csrf.get_token(django_request)),
            T.input(type="hidden",
                    name="subject_user_uuid",
                    value=model.pages.bare_string_id(who._id)),
            T.table(class_="personaldetails")[table_contents]],
        "general_user_profile")]

def configurable_profile_section(who, viewer, django_request):

    profile_fields = all_conf.get('profile_fields')
    variable_sections = T.table[
        [[T.tr[T.th(colspan="2",
                    class_='profile_group',
                    rowspan=str(len(group_fields)))[group_name],
               T.th[group_fields[0]],
               T.td[T.input(type='text',
                            name=group_name+':'+group_fields[0],
                            value=get_profile_subfield_value(who, group_name, group_fields[0]))],
               T.td(rowspan=str(len(group_fields)))[
                   T.div(class_="help")[untemplate.safe_unicode(model.pages.help_for_topic(group_name))]
                   if who.show_help else ""]],
          [[T.tr[T.th[field],
                 T.td[T.input(type='text',
                              name=group_name+':'+field,
                              value=get_profile_subfield_value(who, group_name, field))]]]
           for field in group_fields[1:]]]
         for group_name, group_fields in [(name, profile_fields[name])
                                          for name in all_conf.get('profile_group_order')]]]

    return [model.pages.with_help(viewer,
                                  T.form(action=django.urls.reverse("dashboard:update_configured_profile"),
                                         method='POST')[
                                             variable_sections,
                                             T.input(type="hidden",
                                                     name="csrfmiddlewaretoken",
                                                     value=django.middleware.csrf.get_token(django_request)),
                                             T.input(type="hidden",
                                                     name="subject_user_uuid",
                                                     value=model.pages.bare_string_id(who._id)),
                                             T.input(type='submit',
                                                     value='Update')],
                                  "configurable_profile")]

def misc_section(who, viewer, django_request):
    return [T.ul[T.li["Reset notifications and announcements: ",
                      (T.form(action="/dashboard/reset_messages", method='POST')
                       [T.input(type="hidden",
                                name="csrfmiddlewaretoken",
                                value=django.middleware.csrf.get_token(django_request)),
                        T.input(type='hidden',
                                name='subject_user_uuid',
                                value=model.pages.bare_string_id(who._id)),
                        T.input(type='Reset notifications and announcements',
                                value="Reset notifications")])],
                 T.li["Send password reset email: ",
                      T.form(action=django.urls.reverse("dashboard:send_pw_reset"),
                             method='POST')
                      [T.input(type='hidden',
                               name='subject_user_uuid',
                               value=model.pages.bare_string_id(who._id)),
                       T.input(type="hidden", name="csrfmiddlewaretoken",
                               value=django.middleware.csrf.get_token(django_request)),
                       T.input(type='submit', value="Send password reset")]]]]

def profile_section(who, viewer, django_request):

    result_parts = {'Mugshot': mugshot_section(who, viewer, django_request),
                    'General': general_profile_section(who, viewer, django_request),
                    'Further information': configurable_profile_section(who, viewer, django_request),
                    'Site controls': site_controls_sub_section(who, viewer, django_request),
                    'Availability': availability_sub_section(who, viewer, django_request),
                    'Misc': misc_section(who, viewer, django_request)}
    if 'interest_areas' in all_conf:
        result_parts['Interests and skills'] = model.pages.with_help(viewer,
                                                                     user_interests_section(who, django_request),
                                                                     "interests")
    if 'dietary_avoidances' in all_conf:
        result_parts['Dietary avoidances'] = model.pages.with_help(viewer,
                                                                   avoidances_section(who, django_request),
                                                                   "dietary_avoidances")
    result_sequence = all_conf.get('profile_sections')

    result = T.div(class_="user_profile")[[
        [T.div(class_="profile_subsection",
               id=title.replace(' ', '_'))[T.h3(class_="profile_sub_title")[title],
                                           T.div(class_="profile_sub_body")[result_parts[title]]]]
              for title in result_sequence
              if title in result_parts]]

    return T.div(class_="personal_profile")[result]

def notifications_section(who, viewer, django_request):

    (announcements, _) = who.read_announcements()
    (notifications, _) = who.read_notifications()

    messages = []
    if len(announcements) > 0:
        messages.append(
            [T.h3["Announcements"],
             model.pages.with_help(
                 viewer,
                 T.dl[[[T.dt["From "
                             + model.person.Person.find(bson.objectid.ObjectId(anno['from'])).name()
                             + " at " + model.times.timestring(anno['when'])],
                        T.dd[untemplate.safe_unicode(anno['text'])]]
                       for anno in announcements]],
                 "announcements"),
             T.form(action=django.urls.reverse("dashboard:announcements_read"),
                    method='POST')
             [T.input(type='hidden',
                      name='subject_user_uuid',
                      value=model.pages.bare_string_id(who._id)),
              T.input(type="hidden",
                      name="csrfmiddlewaretoken",
                      value=django.middleware.csrf.get_token(django_request)),
              T.input(type='submit', value="Mark as read")]])
    if len(notifications) > 0:
        messages.append(
            [T.h3["Notifications"],
             model.pages.with_help(viewer,
                                   T.dl[[[T.dt["At "
                                               + model.times.timestring(noti['when'])],
                                          T.dd[untemplate.safe_unicode(noti['text'])]] for noti in notifications]],
                                   "notifications"),
             T.form(action=django.urls.reverse("dashboard:notifications_read"),
                    method='POST')
             [T.input(type='hidden',
                      name='subject_user_uuid',
                      value=model.pages.bare_string_id(who._id)),
              T.input(type="hidden", name="csrfmiddlewaretoken",
                      value=django.middleware.csrf.get_token(django_request)),
              T.input(type='submit', value="Mark as read")]])

    if len(messages) == 0:
        return None
    return messages

def responsibilities(who, viewer, eqtype, django_request):
    type_name = eqtype.pretty_name()
    is_owner = who.is_owner(eqtype)
    has_requested_owner_training = who.has_requested_training([eqtype._id], 'owner')
    owner_section = [T.h4[type_name, " owner information and actions"],
                     (T.div(class_='as_owner')[
                         ([pages.page_pieces.schedule_training_event_form(
                             who, "owner", eqtype, [],
                             "Schedule owner training on " + type_name,
                             django_request),
                           ([T.br,
                             pages.page_pieces.ban_form(eqtype,
                                                        who._id, who.name(),
                                                        'owner',
                                                        django_request)]
                            if viewer.is_administrator()
                            else [])])])
                     if is_owner
                     else [T.p["Not yet an owner of ", type_name,
                               (" but has requested owner training"
                                if has_requested_owner_training
                                else "")],
                           pages.page_pieces.toggle_request(who, eqtype._id, 'owner',
                                                            has_requested_owner_training,
                                                            django_request)]]
    is_trainer, _ = who.is_trainer(eqtype)
    has_requested_trainer_training = who.has_requested_training([eqtype._id], 'trainer')
    trainer_section = [T.h4[type_name, " trainer information and actions"],
                       (T.div(class_='as_trainer')[
                           pages.page_pieces.eqty_training_requests(eqtype, django_request),
                           ([pages.page_pieces.schedule_training_event_form(
                               who, "user", eqtype, [],
                               "Schedule user training on " + type_name,
                               django_request),
                             T.br,
                             pages.page_pieces.schedule_training_event_form(
                                 who, "trainer", eqtype, [],
                                 "Schedule trainer training on  " + type_name,
                                 django_request),
                             ([T.br,
                               pages.page_pieces.ban_form(eqtype,
                                                          who._id, who.name(),
                                                          'trainer',
                                                          django_request)]
                              if viewer.is_administrator()
                              else [])])])
                       if is_trainer
                       else [T.p["Not yet a trainer on ", type_name,
                                 (" but has requested trainer training"
                                  if has_requested_trainer_training
                                  else "")],
                             pages.page_pieces.toggle_request(who, eqtype._id, 'trainer',
                                                              has_requested_trainer_training,
                                                              django_request)]]
    return [T.h3["Responsibilities for ", who.name(),
                     " on equipment of type ", type_name],
                [pages.page_pieces.machinelist(eqtype, who, django_request, is_owner)],
                owner_section,
                trainer_section]

def responsibilities_section(who, viewer, django_request):
    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) == 0:
        return None
    keyed_types = { ty.pretty_name(): ty for ty in their_responsible_types }
    return [T.div(class_="resps")[
        model.pages.with_help(
            viewer,
            [[T.h3[T.a(href=django.urls.reverse('equiptypes:eqty',
                                                args=(keyed_types[name].name,)))[name]],
              responsibilities(who, viewer, keyed_types[name], django_request)]
             for name in sorted(keyed_types.keys())],
            "responsibilities")]]

def equipment_trained_on_section(who, viewer, django_request):
    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    if len(their_equipment_types) == 0:
        return None
    return [T.div(class_='trained_on')[
        model.pages.with_help(viewer,
                              equipment_trained_on(who, viewer,
                                                   their_equipment_types,
                                                   django_request),
                              "equipment_as_user")]]

def other_equipment_section(who, viewer, django_request):
    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    all_remaining_types = ((set(model.equipment_type.Equipment_type.list_equipment_types())
                            -their_responsible_types)
                           -their_equipment_types)
    if len(all_remaining_types) == 0:
        return None
    return [T.div(class_='other_equipment')[
        model.pages.with_help(viewer,
                              pages.page_pieces.general_equipment_list(who, viewer,
                                                                       all_remaining_types,
                                                                       django_request),
                              "other_equipment")]]

def name_of_host(host):
    return model.person.Person.find(host).name() if host else "Unknown"

def equipment_trained_on(who, viewer, equipment_types, django_request):
    keyed_types = { ty.pretty_name():
                    (ty,
                     # the qualification is a pair of (training, untraining)
                     who.qualification(ty.name, 'user'))
                    for ty in equipment_types }
    # keyed_types[name][0] is the equipment type
    # keyed_types[name][1][0] is the qualification
    # keyed_types[name][1][1] is the disqualification
    who_name = who.name()
    return T.div(class_="trainedon")[
        T.table(class_='trainedon')[
            T.thead[T.tr[T.th["Equipment type"],
                         T.th["Trained by"],
                         T.th["Date trained"],
                         T.th["Request trainer training"],
                         T.th["Request owner training"],
                         # todo: put machine statuses in
                         [T.th(class_="ban_form")["Admin: Ban"],
                          T.th(class_="permit_form")["Admin: Make owner"],
                          T.th(class_="permit_form")["Admin: Make trainer"]] if (viewer.is_administrator()
                                                    or viewer.is_owner(name)
                                                    or viewer.is_trainer(name)) else []]],
            T.tbody[[T.tr[T.th[T.a(href=django_request.scheme
                                   + "://" + django_request.META['HTTP_HOST']
                                   + django.urls.reverse("equiptypes:eqty", args=(keyed_types[name][0].name,)))[name]],
                          T.td[", ".join([name_of_host(host)
                                     # todo: linkify these if admin? but that would mean not using the easy "join"
                                                                 for host in keyed_types[name][1][0].hosts])],
                          T.td[model.times.timestring(keyed_types[name][1][0].start)],
                          T.td[pages.page_pieces.toggle_request(who, keyed_types[name][0]._id, 'trainer',
                                                                who.has_requested_training([keyed_types[name][0]._id], 'trainer'),
                                                                django_request)],
                          T.td[pages.page_pieces.toggle_request(who, keyed_types[name][0]._id, 'owner',
                                                                who.has_requested_training([keyed_types[name][0]._id], 'owner'),
                                                                django_request)],
                          ([T.td[pages.page_pieces.ban_form(keyed_types[name][0], who._id, who_name, 'user', django_request)],
                            T.td[pages.page_pieces.permit_form(keyed_types[name][0], who._id, who_name, 'owner', django_request)],
                            T.td[pages.page_pieces.permit_form(keyed_types[name][0], who._id, who_name, 'trainer', django_request)]]
                                                       if (viewer.is_administrator()
                                                           or viewer.is_owner(name)
                                                           or viewer.is_trainer(name)) else [])]
                     for name in sorted(keyed_types.keys())]]]]

def training_requests_section(who, viewer, django_request):
    len_training = len("_training")
    keyed_requests = {req['request_date']: req for req in who.training_requests}
    sorted_requests = [keyed_requests[k] for k in sorted(keyed_requests.keys())]
    return [T.div(class_="requested")[
        T.table()[
            T.thead[T.tr[T.th["Date"],T.th["Equipment"],T.th["Role"]]],
            T.tbody[
                [T.tr[T.td[req['request_date'].strftime("%Y-%m-%d")],
                      T.td[T.a(href=django.urls.reverse("equiptypes:eqty",
                                                        args=(model.equipment_type.Equipment_type.find_by_id(req['equipment_type']).name,)))[model.equipment_type.Equipment_type.find_by_id(req['equipment_type']).pretty_name()]],
                      T.td[str(req['event_type'])[:-len_training]],
                      T.td[pages.page_pieces.cancel_button(who,
                                                           req['equipment_type'],
                                                           'user', "Cancel training request",
                                                           django_request)]]
                 for req in sorted_requests]]]]]

def events_hosting_section(who, viewer, django_request):
    hosting = model.timeline.Timeline.future_events(person_field='hosts', person_id=who._id).events()
    if len(hosting) == 0:
        return None
    return [T.div(class_="hostingevents")[
        pages.event_page.event_table_section(hosting,
                                             who._id,
                                             django_request,
                                             with_completion_link=True)]]

def events_attending_section(who, viewer, django_request):
    attending = model.timeline.Timeline.future_events(person_field='signed_up', person_id=who._id).events()
    if len(attending) == 0:
        return None
    return [model.pages.with_help(viewer,
                                  T.div(class_="attendingingevents")[pages.event_page.event_table_section(attending, who._id, django_request)],
                                  "attending")]

def events_hosted_section(who, viewer, django_request):
    hosted = model.timeline.Timeline.past_events(person_field='hosts', person_id=who._id).events()
    if len(hosted) == 0:
        return None
    return [T.div(class_="hostedevents")[pages.event_page.event_table_section(hosted, who._id, django_request)]]

def events_attended_section(who, viewer, django_request):
    attended = model.timeline.Timeline.past_events(person_field='signed_up', person_id=who._id).events()
    if len(attended) == 0:
        return None
    return [T.div(class_="attendedingevents")[pages.event_page.event_table_section(attended, who._id, django_request)]]

def events_available_section(who, viewer, django_request):
    hosting = model.timeline.Timeline.future_events(person_field='hosts', person_id=who._id).events()
    attending = model.timeline.Timeline.future_events(person_field='signed_up', person_id=who._id).events()
    known_events = hosting + attending
    available_events = [ev
                        for ev in model.timeline.Timeline.future_events().events()
                        if (ev not in known_events
                            and who.satisfies_conditions(ev.attendee_prerequisites))]
    if len(available_events) == 0:
        return None
    return [T.div(class_="availableevents")[
        pages.event_page.event_table_section(
            available_events, # todo: filter this to only those for which the user has the prerequisites
            who._id, django_request, True, True)]]

def create_event_form(viewer, django_request):
    return T.form(action="/makers_admin/create_event",
                  method='GET')[T.table[T.tr[T.th(class_='ralabel')["Event type "],
                                             T.td[pages.page_pieces.event_template_dropdown('event_type')]],
                                        T.tr[T.th(class_='ralabel')["Equipment type "],
                                             T.td[pages.page_pieces.equipment_type_dropdown("equipment_type")]],
                                        # todo: add machine
                                        T.tr[T.th(class_='ralabel')["Start date and time:"],
                                             T.td[T.input(name='start', type='datetime')]],
                                        # todo: add duration
                                        T.tr[T.th(class_='ralabel')["Location"],
                                             T.td[pages.page_pieces.location_dropdown('location')]],
                                        T.tr[T.th(class_='ralabel')["Hosts:"],
                                             T.td[T.input(name='hosts', type='text')]],
                                        T.tr[T.th[""],
                                             T.td[T.input(type='submit', value="Create event")]]],
                                T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request))]

def search_events_form(viewer, django_request):
    # todo: pass the subject user in, and pick that up in the events list, so it can be used for signup
    equip_types = {etype.name: etype.pretty_name()
                       for etype in model.equipment_type.Equipment_type.list_equipment_types()}
    return T.form(action=django.urls.reverse("events:search_events"),
                  # todo: write the receiving function
                  method='GET')[T.form[T.input(type="hidden", name="csrfmiddlewaretoken",
                                               value=django.middleware.csrf.get_token(django_request)),
                                       T.input(type='hidden', name="viewer", value=viewer._id),
                                       T.table[T.tr[T.th(class_='ralabel')["Event type:"],
                                                    T.td[T.input(name='event_type', type='text')]],
                                               T.tr[T.th(class_='ralabel')["Equipment type:"],
                                                    T.td[pages.page_pieces.equipment_type_dropdown("equipment_type")]],
                                               T.tr[T.th(class_='ralabel')["Begins after:"],
                                                    T.td[T.input(name='earliest', type='datetime')]],
                                               T.tr[T.th(class_='ralabel')["Ends before:"],
                                                    T.td[T.input(name='latest', type='datetime')]],
                                               T.tr[T.th(class_='ralabel')[
                                                   T.select(name='person_field')[
                                                       [T.option(value=opt)[opt]
                                                        for opt in ['hosts', 'failed', 'passed', 'noshow', 'signed_up']]]],
                                                    T.td[T.input(name='person_id', type='text')]],
                                               T.tr[T.th(class_='ralabel')["Location"],
                                                    T.td[pages.page_pieces.location_dropdown('location')]],
                                               T.tr[T.th(class_='ralabel')["Include unpublished"],
                                                    T.td[T.input(type='checkbox', name='include_hidden')]],
                                               T.tr[T.td[""],
                                                    T.td[T.input(type='submit', value="Search for events")]]]]]

def announcement_form(viewer, django_request):
    return T.form(action=django.urls.reverse("makers_admin:announce"),
                  method='POST')["Announcement text: ",
                                 T.br,
                                 T.textarea(name='announcement',
                                            cols=80, rows=12),
                                 T.br,
                                 T.input(type="hidden",
                                         name="csrfmiddlewaretoken",
                                         value=django.middleware.csrf.get_token(django_request)),
                                 T.input(type='submit', value="Send announcement")]

def notification_form(viewer, django_request):
    return T.form(action=django.urls.reverse("makers_admin:notify"),
                  method='POST')["Recipient: ", T.input(type='text', name='to'),
                                 T.br,
                                 "Notification text: ",
                                 T.br,
                                 T.textarea(name='message',
                                            cols=80, rows=12),
                                 T.br,
                                 T.input(type="hidden",
                                         name="csrfmiddlewaretoken",
                                         value=django.middleware.csrf.get_token(django_request)),
                                 T.input(type='submit', value="Send notification")]

def email_form(viewer, django_request):
    return T.form(action=django.urls.reverse("makers_admin:send_email"),
                  method='POST')["Recipient: ", T.input(type='text', name='to'),
                                 T.br,
                                 "Subject: ", T.input(type='text', name='subject'),
                                 T.br,
                                 "Notification text: ",
                                 T.br,
                                 T.textarea(name='message',
                                            cols=80, rows=12),
                                 T.br,
                                 T.input(type="hidden",
                                         name="csrfmiddlewaretoken",
                                         value=django.middleware.csrf.get_token(django_request)),
                                 T.input(type='submit', value="Send email")]

def search_users_form(viewer, django_request):
    return model.pages.with_help(
        viewer,
        T.form(action=django.urls.reverse("dashboard:matching_users"),
               method='GET')[T.form["Search for ",
                                    T.input(type='text', name='filter_string'), " as:",
                                    T.ul[[[T.li[T.input(type='radio',
                                                        name='filter_name',
                                                        value=filter_name),
                                                filter_name.capitalize().replace('_', ' ')]
                                         for filter_name in sorted(pages.user_list_page.user_list_filters.keys())]]],
                                    T.input(type="checkbox", name="include_non_members"), "Include non-members",
                                    T.input(type="hidden", name="csrfmiddlewaretoken",
                                            value=django.middleware.csrf.get_token(django_request)),
                                    T.input(type='submit', value="Search for users")]],
        "search_users_form")

def add_user_form(django_request, induction_event_id=None):
    return T.form(action=django.urls.reverse("makers_admin:add_user"),
                  method='POST')[
        T.input(type="hidden", name="csrfmiddlewaretoken",
                value=django.middleware.csrf.get_token(django_request)),
        (T.input(type='hidden', name='induction_event', value=induction_event_id)
         if induction_event_id
         else ""),
        T.table[T.tr[T.th(class_='ralabel')["Given name:"],
                     T.td[T.input(type='text', name='given_name')]],
                T.tr[T.th(class_='ralabel')["Surname:"],
                     T.td[T.input(type='text', name='surname')]],
                T.tr[T.th(class_='ralabel')["Email:"],
                     T.td[T.input(type='text', name='email')]],
                T.tr[T.th(class_='ralabel')["Inducted:"],
                     T.td[T.input(type='checkbox', checked='checked', name='inducted')
                          if induction_event_id
                          else T.input(type='checkbox', name='inducted')]],
                T.tr[T.th[""], T.td[T.input(type='submit', value="Add user")]]]]

def admin_subsection(title, body):
    return T.div(class_='admin_action')[
        T.h3(class_='admin_action_heading')[title],
        T.div(class_='admin_action_body')[body]]

import decouple                 # debug only (at least for now)

def admin_section(who, viewer, django_request):
    return T.div(class_='admin_action_list')[
        admin_subsection("List all users",
                         model.pages.with_help(viewer,
                                               [T.a(href="/dashboard/all")["List all users"]],
                                               "list_all_users")),
        admin_subsection("Member stats",
                         [T.p["Highest membership number is ", str(model.database.get_highest_membership_number())]]),
        admin_subsection("Search for users by characteristic",
                         search_users_form(viewer, django_request)),
        admin_subsection("Create event",
                         model.pages.with_help(
                             viewer,
                             create_event_form(viewer, django_request),
                             "event_creation")),
        admin_subsection("Search for events",
                         model.pages.with_help(
                             viewer,
                             search_events_form(viewer, django_request),
                             "events_search")),
        admin_subsection("Edit event template",
                         model.pages.with_help(
                             viewer,
                             [T.form(action=django.urls.reverse('makers_admin:edit_event_template'),
                                     method='GET')[
                                         T.input(type="hidden", name="csrfmiddlewaretoken",
                                                 value=django.middleware.csrf.get_token(django_request)),
                                         pages.page_pieces.event_template_dropdown('event_template_name'),
                                         T.input(type='submit', value="Edit event template")]],
                             "edit_event_template")),
        admin_subsection("Send announcement", # todo: separate this and control it by whether the person is a trained announcer
                         model.pages.with_help(
                             viewer,
                             announcement_form(viewer, django_request),
                             "send_announcement")),
        admin_subsection("Send notification",
                         model.pages.with_help(
                             viewer,
                             notification_form(viewer, django_request),
                             "send_notification")),
        admin_subsection("Send email as " + model.configuration.get_config('server', 'password_reset_from_address'),
                         model.pages.with_help(
                             viewer,
                             email_form(viewer, django_request),
                             "send_email")),
        admin_subsection("Backup_database",
                         model.pages.with_help(
                             viewer,
                             [T.form(action=django.urls.reverse('makers_admin:backup_database'),
                                     method='GET')[
                                         T.input(type="hidden", name="csrfmiddlewaretoken",
                                                 value=django.middleware.csrf.get_token(django_request)),
                                         T.input(type='submit', value="Backup database")]],
                             "backup_database")),
        admin_subsection("Add user",
                         model.pages.with_help(
                             viewer,
                             add_user_form(django_request),
                             "admin_add_user")),
        admin_subsection("Delete user according to GDPR",
                         model.pages.with_help(
                             viewer,
                             [""],
                             "gdpr_delete_user")),
        admin_subsection("Send test message",
                         [T.form(action=django.urls.reverse("makers_admin:test_message"),
                                 method='POST')[
                                     T.input(type="hidden", name="csrfmiddlewaretoken",
                                             value=django.middleware.csrf.get_token(django_request)),
                                     T.label(for_='to')["To: "],
                                     T.input(type='text', name='to', id='to', value="makers.test.1@makespace.org"),
                                     T.br,
                                     T.label(for_='subject')["Subject: "],
                                     T.input(type='text', name='subject', id='subject', value="Test message sent from the web app"),
                                     T.br,
                                     T.label(for_='message')["Message text: "],
                                     T.input(type='text', name='message', id='subject', value="Test message sent from the web app's admin section"),
                                     T.br,
                                     T.input(type='submit', value="Send test message")]]),
        admin_subsection("Update django logins",
                         model.pages.with_help(
                             viewer,
                             [T.form(action=django.urls.reverse("makers_admin:update_django"),
                                     method='POST')[
                                         T.input(type="hidden", name="csrfmiddlewaretoken",
                                                 value=django.middleware.csrf.get_token(django_request)),
                                         T.input(type='submit', value="Update django logins")]],
                             "admin_update_logins"))]

def add_person_page_contents(page_data, who, viewer, django_request, extra_top_header=None, extra_top_body=None):
    """Add the sections of a user dashboard to a sectional page."""

    if extra_top_body:
        page_data.add_section(extra_top_header or "Confirmation", extra_top_body)

    page_data.add_section("Personal profile", profile_section(who, viewer, django_request))

    messages = notifications_section(who, viewer, django_request)

    if messages:
        page_data.add_section("Notifications",
                              T.div(class_="notifications")[messages],
                              priority=9)

    responsibilities = responsibilities_section(who, viewer, django_request)
    if responsibilities:
        page_data.add_section("Equipment responsibilities", responsibilities)

    trained_on = equipment_trained_on_section(who, viewer, django_request)
    if trained_on:
        if False:
            page_data.add_lazy_section("Equipment I can use", django.urls.reverse('dashboard:trained_on_only'))
        else:
            page_data.add_section("Equipment I can use", trained_on)

    other_equipment = other_equipment_section(who, viewer, django_request)
    if other_equipment:
        page_data.add_section("Other equipment",
                              other_equipment)

    if len(who.training_requests) > 0:
        page_data.add_section("Training requests", training_requests_section(who, viewer, django_request))

    hosting_section = events_hosting_section(who, viewer, django_request)

    if hosting_section:
        page_data.add_section("Events I will be hosting", hosting_section)

    attending_section = events_attending_section(who, viewer, django_request)

    if attending_section:
        page_data.add_section("Events I have signed up for", attending_section)

    hosted_section = events_hosted_section(who, viewer, django_request)

    if hosted_section:
        page_data.add_section("Events I have hosted", hosted_section)

    attended_section = events_attended_section(who, viewer, django_request)

    if attended_section:
        page_data.add_section("Events I have attended", attended_section)

    available_events = events_available_section(who, viewer, django_request)
    if available_events:
        page_data.add_section("Events I can sign up for", available_events)

    if viewer.is_administrator() or viewer.is_auditor():
        page_data.add_section("Admin actions",
                              model.pages.with_help(
                                  viewer,
                                  admin_section(who, viewer, django_request),
                                  "admin"))

    # todo: reinstate when I've created a userapi section in the django setup
    # userapilink = pages.page_pieces.section_link("userapi", who.link_id, who.link_id)
    # api_link = ["Your user API link is ", userapilink]
    # if who.api_authorization is None:
    #     api_link += [T.br,
    #                  "You will need to register to get API access authorization.",
    #                  T.form(action=server_conf['userapi']+"authorize",
    #                         method='POST')[T.button(type="submit", value="authorize")["Get API authorization code"]]]
    # page_data.add_section("API links",
    #                       T.div(class_="apilinks")[api_link])

    return page_data

def person_page_setup():
    global all_conf, server_conf, org_conf
    all_conf = model.configuration.get_config()
    server_conf = all_conf['server']
    org_conf = all_conf['organization']
    pages.page_pieces.set_server_conf()

def person_page_contents(who, viewer, django_request, extra_top_header=None, extra_top_body=None):
    person_page_setup()

    page_data = model.pages.SectionalPage("User dashboard for " + who.name(),
                                          pages.page_pieces.top_navigation(django_request),
                                          viewer=viewer)

    add_person_page_contents(page_data, who, viewer, django_request,
                             extra_top_header=extra_top_header,
                             extra_top_body=extra_top_body)

    return page_data

def profile_sub_page(who, viewer, django_request):
    person_page_setup()

    page_data = model.pages.PageSection("Profile for " + who.name(),
                                        content=profile_section(who, viewer, django_request),
                                        viewer=viewer)

    return page_data.to_string()
