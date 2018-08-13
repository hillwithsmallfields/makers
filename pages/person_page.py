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

all_conf = None
server_conf = None
org_conf = None

def site_controls_sub_section(who, viewer, django_request):
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    # todo: get these from the person's record
    visible_as_host = True
    visible_as_attendee = True
    visible_generally = False
    return T.div(class_="site_options")[
        [T.form(action=base + django.urls.reverse("dashboard:update_site_controls"), method='POST')
         [T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
          T.input(type="hidden", name="subject_user_uuid", value=who._id),
          model.pages.with_help(
              viewer,
              T.table(class_="siteoptions")[
                  T.tr[T.th(class_="ralabel")["Visible as host / owner / trainer to attendees / users"],
                       T.td[T.input(type='checkbox', checked='checked')
                            if visible_as_host
                            else T.input(type='checkbox', name='visible_as_host')]],
                  T.tr[T.th(class_="ralabel")["Visible as attendee / user to hosts / owners / trainers"],
                       T.td[T.input(type='checkbox', checked='checked')
                            if visible_as_attendee
                            else T.input(type='checkbox', name='visible_to_host')]],
                  T.tr[T.th(class_="ralabel")["Visible generally"],
                       T.td[T.input(type='checkbox', name='visible_generally', checked='checked')
                            if visible_generally
                            else T.input(type='checkbox', name='visible_generally')]],
                  T.tr[T.th(class_="ralabel")["Stylesheet"],
                       T.td[T.select(name="stylesheet")[[T.option[style] # todo: mark current stylesheet as checked
                                                         for style in model.configuration.get_stylesheets()]]]],
                  T.tr[T.th(class_="ralabel")["Display help beside forms"],
                       T.td[T.input(type='checkbox', name='display_help', checked='checked')
                            if who.show_help
                            else T.input(type='checkbox', name='display_help')]],
                  T.tr[T.th[""], T.td[T.input(type="submit", value="Update controls")]]],
              "site_controls")]]]

def profile_section(who, viewer, django_request):
    address = who.get_profile_field('address') or {}
    telephone = who.get_profile_field('telephone') or ""
    mugshot = who.get_profile_field('mugshot')
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
                       T.tr[T.th(class_="ralabel")["Telephone"], T.td[T.input(type="text", name="telephone", value=str(telephone))]],
                       T.tr[T.th(class_="ralabel")["Street 1"], T.td[T.input(type="text", name="street_1", value=str(address.get('street_1', "")))]],
                       T.tr[T.th(class_="ralabel")["Street 2"], T.td[T.input(type="text", name="street_2", value=str(address.get('street_2', "")))]],
                       T.tr[T.th(class_="ralabel")["Street 3"], T.td[T.input(type="text", name="street_3", value=str(address.get('street_3', "")))]],
                       T.tr[T.th(class_="ralabel")["City"], T.td[T.input(type="text", name="city", value=str(address.get('city', "")))]],
                       T.tr[T.th(class_="ralabel")["County"], T.td[T.input(type="text", name="county", value=str(address.get('county', "")))]],
                       T.tr[T.th(class_="ralabel")["Country"], T.td[T.input(type="text", name="country", value=str(address.get('country', "")))]],
                       T.tr[T.th(class_="ralabel")["Postcode"], T.td[T.input(type="text", name="postcode", value=str(address.get('postcode', "")))]],
                       T.tr[T.th(class_="ralabel")["No-shows"], T.td[str(len(who.get_noshows()))]],
                       T.tr[T.th(class_="ralabel")["No-show absolutions"], T.td[(T.input(type="text", name="absolutions", value=str(who.noshow_absolutions))
                                                                                 if viewer.is_administrator() else str(who.noshow_absolutions))]],
                       T.tr[T.th[""], T.td[T.input(type="submit", value="Update details")]]],
                   "general_user_profile")],
              T.h2["Site controls"],
              site_controls_sub_section(who, viewer, django_request),
              T.h2["Availability"],
              model.pages.with_help(viewer,
                                    pages.page_pieces.availform(who.available, django_request),
                                    "availability"),
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

def responsibilities(who, viewer, typename, keyed_types, django_request):
    eqtype = keyed_types[typename]
    is_owner = who.is_owner(eqtype)
    has_requested_owner_training = who.has_requested_training([eqtype._id], 'owner')
    is_trainer, _ = who.is_trainer(eqtype)
    has_requested_trainer_training = who.has_requested_training([eqtype._id], 'trainer')
    return [T.h3["Equipment of type " + eqtype.name],
            [pages.page_pieces.machinelist(eqtype, who, django_request, is_owner)],
            T.h3[eqtype.name + " owner information and actions"
                      if is_owner
                      else "Not yet an owner"+(" but has requested owner training" if has_requested_owner_training else "")],
            T.div(class_='as_owner')[([pages.page_pieces.schedule_event_form(who, [T.input(type="hidden", name="event_type", value="owner_training"),
                                                                                   T.input(type="hidden", name="role", value="owner"),
                                                                                   T.input(type="hidden", name="equiptype", value=eqtype._id)],
                                                                             "Schedule owner training",
                                                                             django_request),
                                       [pages.page_pieces.ban_form(eqtype,
                                                                   who._id, who.name(),
                                                                   'owner',
                                                                   django_request) if viewer.is_administrator() else []]]
                                      if is_owner
                                      else pages.page_pieces.toggle_request(who, eqtype._id, 'owner',
                                                                            has_requested_owner_training,
                                                                            django_request))],
            T.h3[eqtype.name + " trainer information and actions"
                      if is_trainer
                      else "Not yet a trainer"+(" but has requested trainer training" if has_requested_trainer_training else "")],
            T.div(class_='as_trainer')[pages.page_pieces.eqty_training_requests(eqtype),
                                       ([pages.page_pieces.schedule_event_form(who,
                                                                               [T.input(type="hidden", name="event_type", value="user_training"),
                                                                                T.input(type="hidden", name="role", value="user"),
                                                                                T.input(type="hidden", name="equiptype", value=eqtype._id)],
                                                                               "Schedule user training",
                                                                               django_request),
                                         pages.page_pieces.schedule_event_form(who,
                                                                               [T.input(type="hidden", name="event_type", value="trainer_training"),
                                                                                T.input(type="hidden", name="role", value="trainer"),
                                                                                T.input(type="hidden", name="equiptype", value=eqtype._id)],
                                                                               "Schedule trainer training",
                                                                               django_request),
                                         [pages.page_pieces.ban_form(eqtype,
                                                                     who._id, who.name(),
                                                                     'trainer',
                                                                     django_request) if viewer.is_administrator() else []]]
                                        if is_trainer
                                        else pages.page_pieces.toggle_request(who, eqtype._id, 'trainer',
                                                                              has_requested_trainer_training,
                                                                              django_request))]]

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
    demographics = who.get_profile_field('demographics') or []
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    return [T.div[[T.form(action=base+"/update/demographics", # todo: get from django reverse
                          method='POST')[T.table[[[T.tr[T.th(class_='ralabel')[aspect],
                                                       T.td[T.input(type='text',
                                                                    name='aspect',
                                                                    value=demographics[aspect])]]]
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
    len_training = len("_training")
    keyed_requests = {req['request_date']: req for req in who.training_requests}
    sorted_requests = [keyed_requests[k] for k in sorted(keyed_requests.keys())]
    return T.div(class_="requested")[T.table()[T.thead[T.tr[T.th["Date"],T.th["Equipment"],T.th["Role"]]],
                                               T.tbody[[T.tr[T.td[req['request_date'].strftime("%Y-%m-%d")],
                                                             T.td[model.equipment_type.Equipment_type.find_by_id(req.get('equipment_type',
                                                                                                                         # todo: remove this back-compat hack
                                                                                                                         req.get('equipment_types', ["dummy"])[0])).pretty_name()],
                                                             T.td[str(req['event_type'])[:-len_training]],
                                                             T.td[pages.page_pieces.cancel_button(who,
                                                                                          req.get('equipment_type',
                                                                                                  # todo: remove this back-compat hack
                                                                                                  req.get('equipment_types',
                                                                                                          ["dummy"])[0]),
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
                         T.dl[[[T.dt["From "
                                     + model.person.Person.find(bson.objectid.ObjectId(anno['from'])).name()
                                     + " at " + model.event.timestring(anno['when'])],
                                T.dd[anno['text']]] for anno in announcements]],
                         T.form(base + "/dashboard/announcements_read", method='POST')
                         [T.input(type='hidden', name='subject_user_uuid', value=who._id),
                          T.input(type="hidden", name="csrfmiddlewaretoken",
                                  value=django.middleware.csrf.get_token(django_request)),
                          T.input(type='hidden', name='upto', value=announcements_upto),
                          T.input(type='submit', value="Mark as read")]])
    if len(notifications) > 0:
        messages.append([T.h3["Notifications"],
                         T.dl[[[T.dt["At " + model.event.timestring(noti['when'])],
                                T.dd[noti['text']]] for noti in notifications]],
                         T.form(base + "/dashboard/notifications_read", method='POST')
                         [T.input(type='hidden', name='subject_user_uuid', value=who._id),
                          T.input(type="hidden", name="csrfmiddlewaretoken",
                                  value=django.middleware.csrf.get_token(django_request)),
                          T.input(type='hidden', name='upto', value=notifications_upto),
                          T.input(type='submit', value="Mark as read")]])

    if len(announcements) > 0 or len(notifications) > 0:
        page_data.add_section("Notifications",
                              model.pages.with_help(viewer,
                                                    T.div(class_="notifications")[messages],
                                                    "notifications"),
                              priority=9)

    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) > 0:
        keyed_types = { ty.pretty_name(): ty for ty in their_responsible_types }
        page_data.add_section("Equipment responsibilities",
                              model.pages.with_help(viewer,
                                                    T.div(class_="resps")[[[T.h2[T.a(href=server_conf['base_url']+server_conf['types']+keyed_types[name].name)[name]],
                                                                            responsibilities(who, viewer, name, keyed_types, django_request)]
                                                                           for name in sorted(keyed_types.keys())]],
                                                    "responsibilities"))

    # print("user types", who.get_equipment_types('user'))
    # print("owner types", who.get_equipment_types('owner'))
    # print("trainer types", who.get_equipment_types('trainer'))

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
    # print("hosting is", hosting)
    if len(hosting) > 0:
        page_data.add_section("Events I will be hosting",
                              T.div(class_="hostingevents")[pages.event_page.event_table_section(hosting, who._id, django_request)])

    attending = model.timeline.Timeline.future_events(person_field='signed_up', person_id=who._id).events
    # print("attending is", attending)
    if len(attending) > 0:
        page_data.add_section("Events I have signed up for",
                              model.pages.with_help(viewer,
                                                    T.div(class_="attendingingevents")[pages.event_page.event_table_section(attending, who._id, django_request)],
                                                    "attending")

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
                              T.div(class_="availableevents")[pages.event_page.event_table_section(available_events, who._id, django_request, True, True)])

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
