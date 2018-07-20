from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import django.middleware.csrf
import model.equipment_type
import model.event
import pages.page_pieces
import model.pages
import model.person
import model.timeline
import model.timeslots
import datetime

all_conf = None
server_conf = None
org_conf = None

def profile_section(who, viewer, django_request):
    form_act = server_conf["update_profile"]
    address = who.get_profile_field('address') or {} # todo: sort out how to get viewer through to this
    telephone = who.get_profile_field('telephone') or ""
    result = [T.form(action=form_act,
                     method='POST')[T.table(class_="personaldetails")[
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
                         T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                         T.input(type="submit", value="Update details")]],
              T.h2["Availability"],
              pages.page_pieces.availform(who.available, django_request)]
    if 'dietary_avoidances' in all_conf:
        result.append([T.h2["Dietary avoidances"], avoidances_section(who, django_request)])
    return T.div(class_="personal_profile")[result]

def responsibilities(who, typename, keyed_types, django_request):
    is_owner = who.is_owner(keyed_types[typename])
    has_requested_owner_training = who.has_requested_training([keyed_types[typename]._id], 'owner')
    eqtype = model.equipment_type.Equipment_type.find(typename)
    is_trainer = who.is_trainer(keyed_types[typename])
    has_requested_trainer_training = who.has_requested_training([keyed_types[typename]._id], 'trainer')
    return [T.h3["Machines"],
            [pages.page_pieces.machinelist(eqtype,
                                     who, is_owner)],
            T.h3["Owner"
                      if is_owner
                      else "Not yet an owner"+(" but has requested owner training" if has_requested_owner_training else "")],
            T.div(class_='as_owner')[(pages.page_pieces.schedule_event_form(who, [T.input(type="hidden", name="event_type", value="training"),
                                                                                  T.input(type="hidden", name="role", value="owner"),
                                                                                  T.input(type="hidden", name="type", value=eqtype._id)],
                                                                            "Schedule owner training",
                                                                            django_request)
                       if is_owner
                       else pages.page_pieces.toggle_request(eqtype, 'owner',
                                                             has_requested_owner_training,
                                                             django_request))],
            T.h3["Trainer"
                      if is_trainer
                      else "Not yet a trainer"+(" but has requested trainer training" if has_requested_trainer_training else "")],
            # todo: count the training requests for this type, and perhaps what times are most popular
                 T.div(class_='as_trainer')[(pages.page_pieces.schedule_event_form(who, [T.input(type="hidden", name="event_type", value="training"),
                                                                                         "User training: ", T.input(type="radio",
                                                                                                                    name="role",
                                                                                                                    value="user",
                                                                                                                    checked="checked"), T.br,
                                                                                         "Trainer training: ", T.input(type="radio",
                                                                                                                       name="role",
                                                                                                                       value="trainer"), T.br,
                                                                                         T.input(type="hidden", name="type", value=eqtype._id)],
                                                                                   "Schedule training",
                                                                                   django_request)
                       if is_trainer
                       else pages.page_pieces.toggle_request(typename, 'trainer',
                                                             has_requested_trainer_training,
                                                             django_request))]]

def avoidances_section(who, django_request):
    if 'dietary_avoidances' not in all_conf:
        return []
    avoidances = who.get_profile_field('avoidances') or []
    form_act = "update/avoidances" # todo: get from config or from django
    return [T.form(action=form_act,
                   method='POST')[T.ul[[T.li[(T.input(type="checkbox", name="dietary", value=thing, checked="checked")[thing]
                                              if thing in avoidances
                                              else T.input(type="checkbox", name="dietary", value=thing)[thing])]
                                        for thing in sorted(all_conf['dietary_avoidances'])]],
                                  T.input(type="hidden", name="csrfmiddlewaretoken", value=django.middleware.csrf.get_token(django_request)),
                                  T.input(type='submit', value="Update avoidances")]]


def equipment_trained_on(who, equipment_types, django_request):
    # todo: handle bans/suspensions, with admin-only buttons to unsuspend them
    keyed_types = { ty.pretty_name(): (ty, who.qualification(ty.name, 'user'))
                    for ty in equipment_types }
    # print "keyed_types are", keyed_types
    # print "sorted(keyed_types.keys()) is", sorted(keyed_types.keys())
    return T.div(class_="trainedon")[
        T.dl[[[T.dt[T.a(href=server_conf['base_url']+server_conf['types']+name)[name]],
               T.dd[ # todo: add when they were trained, and by whom
                   "Since ", model.event.timestring(keyed_types[name][1][0].start), T.br,
                   pages.page_pieces.toggle_request(who, keyed_types[name][0], 'trainer',
                                                    who.has_requested_training([keyed_types[name][0]._id], 'trainer'),
                                                    django_request),
                   pages.page_pieces.toggle_request(who, keyed_types[name][0], 'owner',
                                                    who.has_requested_training([keyed_types[name][0]._id], 'owner'),
                                                    django_request),
                   # todo: add admin-only buttons for suspending qualifications
                   pages.page_pieces.machinelist(keyed_types[name][0],
                                                 who, False)]]
                             for name in sorted(keyed_types.keys())]]]

def training_requests_section(who):
    len_training = len("_training")
    keyed_requests = {req['request_date']: req for req in who.training_requests}
    sorted_requests = [keyed_requests[k] for k in sorted(keyed_requests.keys())]
    return T.div(class_="requested")[T.table()[T.tr[T.th["Date"],T.th["Equipment"],T.th["Role"]],
                                               [T.tr[T.td[req['request_date'].strftime("%Y-%m-%d")],
                                                     T.td[", ".join([model.equipment_type.Equipment_type.find_by_id(id).pretty_name()
                                                                             for id in req['equipment_types']])],
                                                     T.td[str(req['event_type'])[:-len_training]],
                                                     T.td[pages.page_pieces.cancel_button(",".join(map(str, req['equipment_types'])),
                                                                                    'user', "Cancel training request")]]
                                                        for req in sorted_requests]]]


def admin_section(viewer):
    return T.ul[T.li[pages.page_pieces.section_link('admin', "userlist", "User list")],
                T.li[pages.page_pieces.section_link('admin', "intervene", "Create intervention event")]
                        if viewer.is_administrator() else ""]

def add_person_page_contents(page_data, who, viewer, django_request):
    """Add the sections of a user dashboard to a sectional page."""
    page_data.add_section("Personal profile", profile_section(who, viewer, django_request))

    their_responsible_types = set(who.get_equipment_types('owner') + who.get_equipment_types('trainer'))
    if len(their_responsible_types) > 0:
        keyed_types = { ty.pretty_name(): ty for ty in their_responsible_types }
        page_data.add_section("Equipment responsibilities",
                              T.div(class_="resps")[[[T.h2[T.a(href=server_conf['base_url']+server_conf['types']+keyed_types[name].name)[name]],
                                                           responsibilities(who, name, keyed_types, django_request)]
                                                          for name in sorted(keyed_types.keys())]])

    their_equipment_types = set(who.get_equipment_types('user')) - their_responsible_types
    if len(their_equipment_types) > 0:
        page_data.add_section("Equipment trained on",
                              equipment_trained_on(who, their_equipment_types, django_request))

    all_remaining_types = ((set(model.equipment_type.Equipment_type.list_equipment_types())
                            -their_responsible_types)
                           -their_equipment_types)
    if len(all_remaining_types) > 0:
        page_data.add_section("Other equipment",
                              pages.page_pieces.general_equipment_list(who, all_remaining_types, django_request))

    if len(who.training_requests) > 0:
        page_data.add_section("Training requests", training_requests_section(who))

    hosting = model.timeline.Timeline.future_events(person_field='hosts', person_id=who._id).events
    if len(hosting) > 0:
        page_data.add_section("Events I'm hosting",
                              T.div(class_="hostingevents")[pages.page_pieces.eventlist(hosting)])

    attending = model.timeline.Timeline.future_events(person_field='attendees', person_id=who._id).events
    if len(attending) > 0:
        page_data.add_section("Events I'm attending",
                              T.div(class_="attendingingevents")[pages.page_pieces.eventlist(attending)])

    hosted = model.timeline.Timeline.past_events(person_field='hosts', person_id=who._id).events
    if len(hosting) > 0:
        page_data.add_section("Events I have hosted",
                              T.div(class_="hostedevents")[pages.page_pieces.eventlist(hosted)])

    attended = model.timeline.Timeline.past_events(person_field='attendees', person_id=who._id).events
    if len(attended) > 0:
        page_data.add_section("Events I have attended",
                              T.div(class_="attendedingevents")[pages.page_pieces.eventlist(attended)])

    known_events = hosting + attending + hosted + attended
    available_events = [ev
                        for ev in model.timeline.Timeline.future_events().events
                        if ev not in known_events]
    if len(available_events) > 0:
        page_data.add_section("Events I can sign up for",
                              T.div(class_="availableevents")[pages.page_pieces.eventlist(available_events, True)])

    # # todo: I think this condition is giving false positives
    # todo: separate this from django's "admin"
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

def person_page_contents(who, viewer):
    person_page_setup()

    page_data = pages.SectionalPage("User dashboard for " + who.name(),
                                    # todo: put these into a central place, for use on most pages
                                    [T.ul[T.li[T.a(href=org_conf['home_page'])["Home"]],
                                          T.li[T.a(href=org_conf['wiki'])["Wiki"]],
                                          T.li[T.a(href=org_conf['forum'])["Forum"]]]])

    add_person_page_contents(page_data, who, viewer)

    return page_data
