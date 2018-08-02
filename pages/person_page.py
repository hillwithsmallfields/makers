from untemplate.throw_out_your_templates_p3 import htmltags as T
import datetime
import django.middleware.csrf
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
                       T.tr[T.th(class_="ralabel")["Stylesheet"], T.td[T.input(type="text", # todo: make this a dropdown
                                                                               name="stylesheet", value=who.stylesheet or "makers")]],
                       T.tr[T.th[""], T.td[T.input(type="submit", value="Update details")]]],
                   "general_user_profile")],
              T.h2["Availability"],
              model.pages.with_help(pages.page_pieces.availform(who.available, django_request),
                                    "availability")]
    if 'skill_areas' in all_conf:
        result.append([T.h2["Skills and interests"], model.pages.with_help(skills_section(who, django_request),
                                                                           "skills_interests")])
    if 'dietary_avoidances' in all_conf:
        result.append([T.h2["Dietary avoidances"], model.pages.with_help(avoidances_section(who, django_request),
                                                                         "dietary_avoidances")])
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
            T.div(class_='as_owner')[([pages.page_pieces.schedule_event_form(who, [T.input(type="hidden", name="event_type", value="training"),
                                                                                   T.input(type="hidden", name="role", value="owner"),
                                                                                   T.input(type="hidden", name="type", value=eqtype._id)],
                                                                             "Schedule owner training",
                                                                             django_request),
                                       [pages.page_pieces.ban_form(eqtype, who, 'owner', django_request) if viewer.is_administrator() else []]]
                                      if is_owner
                                      else pages.page_pieces.toggle_request(who, eqtype._id, 'owner',
                                                                            has_requested_owner_training,
                                                                            django_request))],
            T.h3[eqtype.name + " trainer information and actions"
                      if is_trainer
                      else "Not yet a trainer"+(" but has requested trainer training" if has_requested_trainer_training else "")],
            T.div(class_='as_trainer')[pages.page_pieces.eqty_training_requests(eqtype),
                                       ([pages.page_pieces.schedule_event_form(who,
                                                                               [T.input(type="hidden", name="event_type", value="training"),
                                                                                "User training: ", T.input(type="radio",
                                                                                                           name="role",
                                                                                                           value="user",
                                                                                                           checked="checked"), T.br,
                                                                                "Trainer training: ", T.input(type="radio",
                                                                                                              name="role",
                                                                                                              value="trainer"), T.br,
                                                                                T.input(type="hidden", name="equiptype", value=eqtype._id)],
                                                                               "Schedule training",
                                                                               django_request),
                                         [pages.page_pieces.ban_form(eqtype, who, 'trainer', django_request) if viewer.is_administrator() else []]]
                                        if is_trainer
                                        else pages.page_pieces.toggle_request(who, eqtype._id, 'trainer',
                                                                              has_requested_trainer_training,
                                                                              django_request))]]

def skills_button(area_name, level, which_level):
    return [T.td[T.input(type='radio',
                         name=area_name,
                         value=str(which_level),
                         checked='checked')
                 if level == which_level
                 else T.input(type='radio',
                              name=area_name,
                              value=str(which_level))]]

def skills_section(who, django_request):
    skill_levels = who.get_profile_field('skill_levels') or {}
    skill_areas = all_conf.get('skill_areas', None)
    if skill_areas is None:
        return []
    existing_skills = {area_name: skill_levels.get(area_name, 0) for area_name in skill_areas}
    return [T.form(action="update_levels", method="POST")
            [T.table[T.thead[T.tr[[T.th["Area"], T.th["0"], T.th["1"], T.th["2"], T.th["3"]]]],
                     T.tbody[[[T.tr[T.th[area],
                                    skills_button(area, existing_skills[area], 0),
                                    skills_button(area, existing_skills[area], 1),
                                    skills_button(area, existing_skills[area], 2),
                                    skills_button(area, existing_skills[area], 3)]]
                              for area in sorted(skill_areas)]]],
             T.div(align="right")[T.input(type="submit", value="Update interests and skills")]]]

def avoidances_section(who, django_request):
    if 'dietary_avoidances' not in all_conf:
        return []
    avoidances = who.get_profile_field('avoidances') or []
    return [T.form(action="update/avoidances",# todo: get from config or from django
                   method='POST')[T.ul[[T.li[(T.input(type="checkbox", name="dietary", value=thing, checked="checked")[thing]
                                              if thing in avoidances
                                              else T.input(type="checkbox", name="dietary", value=thing)[thing])]
                                        for thing in sorted(all_conf['dietary_avoidances'])]],
                                  T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                  T.div(align="right")[T.input(type='submit', value="Update avoidances")]]]

def name_of_host(host):
    return model.person.Person.find(host).name() if host else "Unknown"

def equipment_trained_on(who, viewer, equipment_types, django_request):
    keyed_types = { ty.pretty_name(): (ty, who.qualification(ty.name, 'user'))
                    for ty in equipment_types }
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST'] + django.urls.reverse("equiptypes:eqty")
    return T.div(class_="trainedon")[
        T.table(class_='trainedon')[
            T.thead[T.tr[T.th["Equipment type"],
                         T.th["Trainer"],
                         T.th["Date"],
                         # todo: put machine statuses in
                         [T.th["Ban"],
                          T.th["Make owner"],
                          T.th["Make trainer"]] if (viewer.is_administrator()
                                                    or viewer.is_owner(name)
                                                    or viewer.is_trainer(name)) else []]],
            T.tbody[[T.tr[T.th[T.a(href=base + django.urls.reverse("equiptypes") + keyed_types[name][0].name)[name]],
                          T.td[join([name_of_host(host)
                                     # todo: linkify these if admin? but that would mean not using the easy "join"
                                                                 for host in keyed_types[name][1][0].hosts])],
                          T.td[model.event.timestring(keyed_types[name][1][0].start)],
                          T.td[pages.page_pieces.toggle_request(who, keyed_types[name][0]._id, 'trainer',
                                                                who.has_requested_training([keyed_types[name][0]._id], 'trainer'),
                                                                django_request)],
                          T.td[pages.page_pieces.toggle_request(who, keyed_types[name][0]._id, 'owner',
                                                                who.has_requested_training([keyed_types[name][0]._id], 'owner'),
                                                                django_request)],
                          ([T.td[pages.page_pieces.ban_form(keyed_types[name][0], who, 'user', django_request)],
                            T.td[pages.page_pieces.permit_form(keyed_types[name][0], who, 'owner', django_request)],
                            T.td[pages.page_pieces.permit_form(keyed_types[name][0], who, 'trainer', django_request)]]
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


def admin_section(viewer):
    return T.ul[T.li[pages.page_pieces.section_link('admin', "userlist", "User list")],
                # T.li["Search by name:", T.form()[]],
                T.li[pages.page_pieces.section_link('admin', "intervene", "Create intervention event")]
                        if viewer.is_administrator() else ""]

def add_person_page_contents(page_data, who, viewer, django_request, extra_top_header=None, extra_top_body=None):
    """Add the sections of a user dashboard to a sectional page."""

    if extra_top_body:
        page_data.add_section(extra_top_header or "Confirmation", extra_top_body)

    page_data.add_section("Personal profile", profile_section(who, viewer, django_request))

    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) > 0:
        keyed_types = { ty.pretty_name(): ty for ty in their_responsible_types }
        page_data.add_section("Equipment responsibilities",
                              T.div(class_="resps")[[[T.h2[T.a(href=server_conf['base_url']+server_conf['types']+keyed_types[name].name)[name]],
                                                           responsibilities(who, viewer, name, keyed_types, django_request)]
                                                          for name in sorted(keyed_types.keys())]])

    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    if len(their_equipment_types) > 0:
        page_data.add_section("Equipment trained on",
                              equipment_trained_on(who, viewer, their_equipment_types, django_request))

    all_remaining_types = ((set(model.equipment_type.Equipment_type.list_equipment_types())
                            -their_responsible_types)
                           -their_equipment_types)
    if len(all_remaining_types) > 0:
        page_data.add_section("Other equipment",
                              pages.page_pieces.general_equipment_list(who, viewer, all_remaining_types, django_request))

    if len(who.training_requests) > 0:
        page_data.add_section("Training requests", training_requests_section(who, django_request))

    hosting = model.timeline.Timeline.future_events(person_field='hosts', person_id=who._id).events
    if len(hosting) > 0:
        page_data.add_section("Events I'm hosting",
                              T.div(class_="hostingevents")[pages.event_page.event_table_section(hosting, who._id, django_request)])

    attending = model.timeline.Timeline.future_events(person_field='attendees', person_id=who._id).events
    if len(attending) > 0:
        page_data.add_section("Events I'm attending",
                              T.div(class_="attendingingevents")[pages.event_page.event_table_section(attending, who._id, django_request)])

    hosted = model.timeline.Timeline.past_events(person_field='hosts', person_id=who._id).events
    if len(hosting) > 0:
        page_data.add_section("Events I have hosted",
                              T.div(class_="hostedevents")[pages.event_page.event_table_section(hosted, who._id, django_request)])

    attended = model.timeline.Timeline.past_events(person_field='attendees', person_id=who._id).events
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

    # todo: I think this condition is giving false positives
    # todo: separate this from django's "admin", and make an app for it
    # if viewer.is_administrator() or viewer.is_auditor():
    #     page_data.add_section("Admin actions",
    #                           admin_section(viewer))

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

def person_page_contents(who, viewer, extra_top_header=None, extra_top_body=None):
    person_page_setup()

    page_data = pages.SectionalPage("User dashboard for " + who.name(),
                                    # todo: put these into a central place, for use on most pages
                                    [T.ul[T.li[T.a(href=org_conf['home_page'])["Home"]],
                                          T.li[T.a(href=org_conf['wiki'])["Wiki"]],
                                          T.li[T.a(href=org_conf['forum'])["Forum"]]]],
                                    viewer=viewer)

    add_person_page_contents(page_data, who, viewer,
                             extra_top_header=extra_top_header,
                             extra_top_body=extra_top_body)

    return page_data
