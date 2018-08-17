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
import untemplate.throw_out_your_templates_p3 as untemplate

all_conf = None
server_conf = None
org_conf = None

def visibility_radio(label, visibility):
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
            "No", (T.input(type='radio',
                           name=label,
                           value='yes',
                           checked='checked')
                   if visibility == True
                   else T.input(type='radio',
                                name=label,
                                value='yes'))]

def site_controls_sub_section(who, viewer, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    # todo: get these from the person's record
    return T.div(class_="site_options")[
        [T.form(action=base + django.urls.reverse("dashboard:update_site_controls"), method='POST')
         [T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
          T.input(type="hidden", name="subject_user_uuid", value=who._id),
          model.pages.with_help(
              viewer,
              T.table(class_="siteoptions")[
                  T.tr[T.th(class_="ralabel")["Visible as host / owner / trainer to attendees / users"],
                       T.td[visibility_radio("host", who.visibility['visibility_as_host'])]],
                  T.tr[T.th(class_="ralabel")["Visible as attendee / user to hosts / owners / trainers"],
                       T.td[visibility_radio("attendee", who.visibility['visibility_as_attendee'])]],
                  T.tr[T.th(class_="ralabel")["Visible generally"],
                       T.td[visibility_radio("general", who.visibility['visibility_in_general'])]],
                  T.tr[T.th(class_="ralabel")["Stylesheet"],
                       T.td[T.select(name='stylesheet')[[T.option[style] # todo: mark current stylesheet as checked
                                                         for style in model.configuration.get_stylesheets()]]]],
                  T.tr[T.th(class_="ralabel")["Display help beside forms"],
                       T.td[T.input(type='checkbox', name='display_help', checked='checked')
                            if who.show_help
                            else T.input(type='checkbox', name='display_help')]],
                  T.tr[T.th(class_="ralabel")["Notify training etc by email"],
                       T.td[T.input(type='checkbox', name='notify_by_email', checked='checked')
                            if self.notify_by_email
                            else T.input(type='checkbox', name='notify_by_email')]],
                  T.tr[T.th(class_="ralabel")["Notify training etc in site"],
                       T.td[T.input(type='checkbox', name='notify_in_site', checked='checked')
                            if self.notify_by_email
                            else T.input(type='checkbox', name='notify_in_site')]],
                  T.tr[T.th[""], T.td[T.input(type="submit", value="Update controls")]]],
              "site_controls")]]]

def get_profile_subfield_value(who, group_name, name):
    group = who.get_profile_field(group_name)
    if type(group) != dict:
        return ""
    return group.get(name, "")

def profile_section(who, viewer, django_request):

    profile_fields = all_conf.get('profile_fields')
    print("variable profile fields are", profile_fields)

    variable_sections = [[T.tr[T.th(colspan="2", rowspan=str(len(group_fields)))[group_name],
                               T.th[group_fields[0]],
                               T.td[T.input(type='text',
                                            name=group_name+':'+group_fields[0],
                                            value=get_profile_subfield_value(who, group_name, group_fields[0]))],
                               T.td(rowspan=str(len(group_fields)))[
                                   untemplate.safe_unicode(model.pages.help_for_topic(group_name))]],
                          [[T.tr[T.th[field],
                                 T.td[T.input(type='text',
                                              name=group_name+':'+field,
                                              value=get_profile_subfield_value(who, group_name, field))]]]
                           for field in group_fields[1:]]]
                         for group_name, group_fields in profile_fields]

    address = who.get_profile_field('address') or {}
    telephone = who.get_profile_field('telephone') or ""
    mugshot = who.get_profile_field('mugshot')
    _, timeslot_times, _ = model.timeslots.get_slots_conf()
    timeslot_times = {'morning_start': str(timeslot_times['morning'][0]),
                      'morning_end': str(timeslot_times['morning'][1]),
                      'afternoon_start': str(timeslot_times['afternoon'][0]),
                      'afternoon_end': str(timeslot_times['afternoon'][1]),
                      'evening_start': str(timeslot_times['evening'][0]),
                      'evening_end': str(timeslot_times['evening'][1])}
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    result = [T.form(action=base + django.urls.reverse("dashboard:update_mugshot"), method='POST')
              [T.img(src=mugshot) if mugshot else "",
               "Upload new photo: ", T.input(type="text"),
               T.input(type="hidden", name="subject_user_uuid", value=who.link_id),
               T.input(type="submit", value="Update photo")],
              T.form(action=base + django.urls.reverse("dashboard:update_profile"), method='POST')
              [T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
               T.input(type="hidden", name="subject_user_uuid", value=who._id),
               model.pages.with_help(
                   viewer,
                   T.table(class_="personaldetails")[
                       T.tr[T.th(class_="ralabel")["Name"], T.td[T.input(type="text",
                                                                         name="name",
                                                                         value=who.name())]],
                       T.tr[T.th(class_="ralabel")["email"], T.td[T.input(type="email",
                                                                          name="email",
                                                                          value=who.get_email())]],
                       T.tr[T.th(class_="ralabel")["Membership number"], T.td[str(who.membership_number)]],
                       T.tr[T.th(class_="ralabel")['Fob number'],
                            T.td[(T.input(type="text",
                                          name="fob",
                                          value=str(who.fob))
                                  if viewer.is_administrator()
                                  else [str(who.fob)])]],
                       T.tr[T.th(class_="ralabel")["link-id"], T.td[str(who.link_id)]],
                       T.tr[T.th(class_="ralabel")["No-shows"], T.td[str(len(who.get_noshows()))]],
                       T.tr[T.th(class_="ralabel")["No-show absolutions"], T.td[(T.input(type="text",
                                                                                         name="absolutions",
                                                                                         value=str(who.noshow_absolutions))
                                                                                 if viewer.is_administrator() else str(who.noshow_absolutions))]],
                       T.tr[T.th[""], T.td[T.input(type="submit", value="Update details")]]],
                   "general_user_profile"),
               model.pages.with_help(viewer,
                                     T.form(action=base + django.urls.reverse("dashboard:update_configured_profile"),
                                            method='POST')[variable_sections,
                                                           T.input(type="hidden",
                                                                   name="csrfmiddlewaretoken",
                                                                   value=django.middleware.csrf.get_token(django_request)),
                                                           T.input(type="hidden",
                                                                   name="subject_user_uuid",
                                                                   value=who._id),
                                                           T.input(type='submit',
                                                                   value='Update')],
                                     "configurable_profile"],
              T.h2["Site controls"],
              site_controls_sub_section(who, viewer, django_request),
              T.h2["Availability"],
              model.pages.with_help(viewer,
                                    pages.page_pieces.availform(who.available, django_request),
                                    "availability",
                                    timeslot_times),
              T.h2["Misc"],
              T.ul[T.li["Reset notifications and announcements: ",
                        (T.form(action=base + "/dashboard/reset_messages", method='POST')
                         [T.input(type="hidden",
                                  name="csrfmiddlewaretoken",
                                  value=django.middleware.csrf.get_token(django_request)),
                          T.input(type='hidden', name='subject_user_uuid', value=who._id),
                          T.input(type='submit',
                                  value="Reset notifications")])]]]
    if 'skill_areas' in all_conf:
        result.append([T.h2["Skills and interests"],
                       model.pages.with_help(viewer,
                                             user_skills_section(who, django_request),
                                             "skills_interests")])
    if 'dietary_avoidances' in all_conf:
        result.append([T.h2["Dietary avoidances"],
                       model.pages.with_help(viewer,
                                             avoidances_section(who, django_request),
                                             "dietary_avoidances")])
    if 'demographics' in all_conf:
        result.append([T.h2["Demographics"],
                       model.pages.with_help(viewer,
                                             demographics_section(who, django_request),
                                             "demographics")])

    return T.div(class_="personal_profile")[result]

def responsibilities(who, viewer, eqtype, django_request):
    type_name = eqtype.pretty_name()
    is_owner = who.is_owner(eqtype)
    has_requested_owner_training = who.has_requested_training([eqtype._id], 'owner')
    owner_section = [T.h4[type_name, " owner information and actions"],
                     (T.div(class_='as_owner')[
                         ([pages.page_pieces.schedule_event_form(
                             who, [T.input(type="hidden", name="event_type", value="owner_training"),
                                   T.input(type="hidden", name="role", value="owner"),
                                   T.input(type="hidden", name="equiptype", value=eqtype._id)],
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
                           pages.page_pieces.eqty_training_requests(eqtype),
                           ([pages.page_pieces.schedule_event_form(
                               who,
                               [T.input(type="hidden", name="event_type", value="user_training"),
                                T.input(type="hidden", name="role", value="user"),
                                T.input(type="hidden", name="equiptype", value=eqtype._id)],
                               "Schedule user training on " + type_name,
                               django_request),
                             T.br,
                             pages.page_pieces.schedule_event_form(
                                 who,
                                 [T.input(type="hidden", name="event_type", value="trainer_training"),
                                  T.input(type="hidden", name="role", value="trainer"),
                                  T.input(type="hidden", name="equiptype", value=eqtype._id)],
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

def user_skills_section(who, django_request):
    return pages.page_pieces.skills_section(who.get_profile_field('skill_levels') or {},
                                            who.get_profile_field('interest_emails', [False, False, False]),
                                            django_request)

def avoidances_section(who, django_request):
    if 'dietary_avoidances' not in all_conf:
        return []
    avoidances = who.get_profile_field('avoidances') or []
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return [T.form(action=base+"/update/avoidances",# todo: get from django reverse
                   method='POST')[T.ul[[T.li[(T.input(type="checkbox", name="dietary", value=thing, checked="checked")[thing]
                                              if thing in avoidances
                                              else T.input(type="checkbox", name="dietary", value=thing)[thing])]
                                        for thing in sorted(all_conf['dietary_avoidances'])]],
                                  T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                  T.div(align="right")[T.input(type='submit', value="Update avoidances")]]]

def demographics_section(who, django_request):
    if 'demographics' not in all_conf:
        return []
    demographics_aspects = all_conf['demographics']
    demographics = who.get_profile_field('demographics') or {}
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return [T.div[[T.form(action=base+"/update/demographics", # todo: get from django reverse
                          method='POST')[T.table[[[T.tr[T.th(class_='ralabel')[aspect],
                                                       T.td[T.input(type='text',
                                                                    name='aspect',
                                                                    value=demographics.get(aspect, ""))]]]
                                                  for aspect in demographics_aspects],
                                                 T.tr[T.td[""],
                                                      T.input(type='submit',
                                                              value="update demographic information")]]]]]]

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
                          T.td[model.event.timestring(keyed_types[name][1][0].start)],
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

def training_requests_section(who, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    len_training = len("_training")
    keyed_requests = {req['request_date']: req for req in who.training_requests}
    sorted_requests = [keyed_requests[k] for k in sorted(keyed_requests.keys())]
    return T.div(class_="requested")[T.table()[T.thead[T.tr[T.th["Date"],T.th["Equipment"],T.th["Role"]]],
                                               T.tbody[[T.tr[T.td[req['request_date'].strftime("%Y-%m-%d")],
                                                             T.td[T.a(href=base+django.urls.reverse("equiptypes:eqty",
                                                                                                    args=(model.equipment_type.Equipment_type.find_by_id(req['equipment_type']).name,)))[model.equipment_type.Equipment_type.find_by_id(req['equipment_type']).pretty_name()]],
                                                             T.td[str(req['event_type'])[:-len_training]],
                                                             T.td[pages.page_pieces.cancel_button(who,
                                                                                                  req['equipment_type'],
                                                                                                  'user', "Cancel training request",
                                                                                                  django_request)]]
                                                        for req in sorted_requests]]]]

def create_event_form(viewer, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    template_types = {template['name']: template['event_type']
                      for template in model.event.Event.list_templates([], None)}
    equip_types = {etype.name: etype.pretty_name()
                       for etype in model.equipment_type.Equipment_type.list_equipment_types()}
    return T.form(action=base+"/makers_admin/create_event",
                  method='GET')["Event type ",
                                T.select(name='template_name')[[[T.option(value=tt)[template_types[tt]]]
                                                                for tt in sorted(template_types.keys())]],
                                " on equipment type ",
                                T.select(name='equipment_type')[[[T.option(value=et)[equip_types[et]]]
                                                                 for et in sorted(equip_types.keys())]],
                                T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                T.input(type='submit', value="Create event")]

def announcement_form(viewer, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return T.form(action=base+"/makers_admin/announce", # todo: use reverse
                  method='POST')["Announcement text: ",
                                 T.textarea(name='announcement'),
                                 T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                 T.input(type='submit', value="Send announcement")]

def notification_form(viewer, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return T.form(action=base+"/makers_admin/notify", # todo: use reverse
                  method='POST')["Recipient: ", T.input(type='text', name='to'),
                                 "Notification text: ",
                                 T.textarea(name='message'),
                                 T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                 T.input(type='submit', value="Send announcement")]

def admin_section(viewer, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return T.ul[T.li[T.a(href=base+"/dashboard/all")["List all users"], " (may be slow and timeout on server)"],
                T.li["Search by name:", T.form(action=base + "/dashboard/match",
                                               method='GET')[T.form[T.input(type='text', name='pattern'),
                                                                    T.input(type='submit', value='Search')]]],
                T.li["Create event: ",
                      create_event_form(viewer, django_request)],
                T.li["Send announcement: ", # todo: separate this and control it by whether the person is a trained announcer
                     announcement_form(viewer, django_request)],
                T.li["Send notification: ",
                     notification_form(viewer, django_request)]]

def add_person_page_contents(page_data, who, viewer, django_request, extra_top_header=None, extra_top_body=None):
    """Add the sections of a user dashboard to a sectional page."""

    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']

    if extra_top_body:
        page_data.add_section(extra_top_header or "Confirmation", extra_top_body)

    page_data.add_section("Personal profile", profile_section(who, viewer, django_request))

    (announcements, announcements_upto) = who.read_announcements()
    (notifications, notifications_upto) = who.read_notifications()

    messages = []
    if len(announcements) > 0:
        messages.append([T.h3["Announcements"],
                         model.pages.with_help(viewer,
                                               T.dl[[[T.dt["From "
                                                           + model.person.Person.find(bson.objectid.ObjectId(anno['from'])).name()
                                                           + " at " + model.event.timestring(anno['when'])],
                                                      T.dd[untemplate.safe_unicode(anno['text'])]] for anno in announcements]],
                                               "announcements"),
                         T.form(base + "/dashboard/announcements_read", method='POST')
                         [T.input(type='hidden', name='subject_user_uuid', value=who._id),
                          T.input(type="hidden", name="csrfmiddlewaretoken",
                                  value=django.middleware.csrf.get_token(django_request)),
                          T.input(type='hidden', name='upto', value=announcements_upto),
                          T.input(type='submit', value="Mark as read")]])
    if len(notifications) > 0:
        messages.append([T.h3["Notifications"],
                         model.pages.with_help(viewer,
                                               T.dl[[[T.dt["At " + model.event.timestring(noti['when'])],
                                                      T.dd[untemplate.safe_unicode(noti['text'])]] for noti in notifications]],
                                               "notifications"),
                         T.form(base + "/dashboard/notifications_read", method='POST')
                         [T.input(type='hidden', name='subject_user_uuid', value=who._id),
                          T.input(type="hidden", name="csrfmiddlewaretoken",
                                  value=django.middleware.csrf.get_token(django_request)),
                          T.input(type='hidden', name='upto', value=notifications_upto),
                          T.input(type='submit', value="Mark as read")]])

    if len(announcements) > 0 or len(notifications) > 0:
        page_data.add_section("Notifications",
                              T.div(class_="notifications")[messages],
                              priority=9)

    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) > 0:
        keyed_types = { ty.pretty_name(): ty for ty in their_responsible_types }
        page_data.add_section("Equipment responsibilities",
                              [T.div(class_="resps")[model.pages.with_help(
                                  viewer,
                                  [[T.h3[T.a(href=server_conf['base_url']+server_conf['types']+keyed_types[name].name)[name]],
                                    responsibilities(who, viewer, keyed_types[name], django_request)]
                                   for name in sorted(keyed_types.keys())],
                                  "responsibilities")]])

    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    if len(their_equipment_types) > 0:
        page_data.add_section("Equipment I can use",
                              model.pages.with_help(viewer,
                                                    equipment_trained_on(who, viewer, their_equipment_types, django_request),
                                                    "equipment_as_user"))

    all_remaining_types = ((set(model.equipment_type.Equipment_type.list_equipment_types())
                            -their_responsible_types)
                           -their_equipment_types)
    if len(all_remaining_types) > 0:
        page_data.add_section("Other equipment",
                              model.pages.with_help(viewer,
                                                    pages.page_pieces.general_equipment_list(who, viewer, all_remaining_types, django_request),
                                                    "other_equipment"))

    if len(who.training_requests) > 0:
        page_data.add_section("Training requests", training_requests_section(who, django_request))

    hosting = model.timeline.Timeline.future_events(person_field='hosts', person_id=who._id).events
    if len(hosting) > 0:
        page_data.add_section(
            "Events I will be hosting",
            T.div(class_="hostingevents")[
                pages.event_page.event_table_section(hosting,
                                                     who._id,
                                                     django_request,
                                                     with_completion_link=True)])

    attending = model.timeline.Timeline.future_events(person_field='signed_up', person_id=who._id).events
    if len(attending) > 0:
        page_data.add_section("Events I have signed up for",
                              model.pages.with_help(viewer,
                                                    T.div(class_="attendingingevents")[pages.event_page.event_table_section(attending, who._id, django_request)],
                                                    "attending"))

    hosted = model.timeline.Timeline.past_events(person_field='hosts', person_id=who._id).events
    if len(hosting) > 0:
        page_data.add_section("Events I have hosted",
                              T.div(class_="hostedevents")[pages.event_page.event_table_section(hosted, who._id, django_request)])

    attended = model.timeline.Timeline.past_events(person_field='signed_up', person_id=who._id).events
    if len(attended) > 0:
        page_data.add_section("Events I have attended",
                              T.div(class_="attendedingevents")[pages.event_page.event_table_section(attended, who._id, django_request)])

    known_events = hosting + attending + hosted + attended
    available_events = [ev
                        for ev in model.timeline.Timeline.future_events().events
                        if ev not in known_events]
    if len(available_events) > 0:
        page_data.add_section("Events I can sign up for",
                              T.div(class_="availableevents")[
                                  pages.event_page.event_table_section(
                                      available_events, # todo: filter this to only those for which the user has the prerequisites
                                      who._id, django_request, True, True)])

    if viewer.is_administrator() or viewer.is_auditor():
        page_data.add_section("Admin actions",
                              admin_section(viewer, django_request))

    # todo: reinstate when I've created a userapi section in the django setup
    # userapilink = pages.page_pieces.section_link("userapi", who.link_id, who.link_id)
    # api_link = ["Your user API link is ", userapilink]
    # if who.api_authorization is None:
    #     api_link += [T.br,
    #                  "You will need to register to get API access authorization.",
    #                  T.form(action=server_conf['base_url']+server_conf['userapi']+"authorize",
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
