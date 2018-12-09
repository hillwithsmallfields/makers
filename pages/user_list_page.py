from untemplate.throw_out_your_templates_p3 import htmltags as T

import django.urls
import model.access_permissions as access_permissions
import model.configuration as configuration
import model.person as person
import model.event
import re

serverconf=None

def equipment_type_role_name_list(who, role):
    """Return a list of equipment types for which a person has a given role."""
    # todo: make this into a list of names with individual anchors
    return ", ".join(sorted(who.get_equipment_type_names(role)))

def flagstring(who):
    return (("A" if who.is_active() else "a")
            + ("P" if who.password_is_usable() else "p")
            + ("S" if who.is_django_staff() else "s")
            )

def user_list_section(django_request,
                      include_non_members=False,
                      filter_fn=None, filter_opaque=None):
    """Return the users list, if the viewing person is allowed to see it.
    Otherwise, just how many people there are.
    The optional first argument is a flag for whether to include non-members.
    The optional second argument is a boolean function taking a person object,
    returning whether to include them in the list.  This could be used for things
    like listing people whose fobs are ready for enabling, or who have missed
    paying their latest subscription.  A third argument is passed through
    to that function."""
    global serverconf
    if serverconf == None:
        serverconf = configuration.get_config()['server']
    viewing_user = model.person.Person.find(django_request.user.link_id)
    people = person.Person.list_all_people() if include_non_members else person.Person.list_all_members()
    if filter_fn:
        people = [someone for someone in people if filter_fn(someone, filter_opaque)]
    people_dict = {whoever.name(): whoever for whoever in people}
    if viewing_user.is_auditor() or viewing_user.is_admin():
        return T.table[[T.tr[T.th(class_='mem_num')["Mem #"],
                             T.th(class_='username')["Name"],
                             T.th(class_='loginh')["Login"],
                             T.th(class_='flagsh')["Flags"],
                             T.th(class_='email')["Email"],
                             T.th(class_='user')["User"],
                             T.th(class_='owner')["Owner"],
                             T.th(class_='trainer')["Trainer"],
                             T.th(class_='note')["Notes"]]],
                       [T.tr[T.td(class_='mem_num')[str(who.membership_number)],
                             T.th(class_='username')[T.a(href=django.urls.reverse('dashboard:user_dashboard', args=([who.link_id])))[whoname]],
                             T.td(class_='login')[who.get_login_name() or ""],
                             T.td(class_='flags')[flagstring(who)],
                             T.td(class_='email')[T.a(href="mailto:"+who.get_email() or "")[who.get_email() or ""]],
                             T.td(class_='user')[equipment_type_role_name_list(who, 'user')],
                             T.td(class_='owner')[equipment_type_role_name_list(who, 'owner')],
                             T.td(class_='trainer')[equipment_type_role_name_list(who, 'trainer')],
                             T.td(class_='note')[T.form()[who.get_admin_note() or ""]]]
                        for (whoname, who) in [(key, people_dict[key]) for key in sorted(people_dict.keys())]
                    ]]
    else:
        return T.p["There are "+str(len(people))
                   +(" people" if include_non_members else " members")
                   +" in the database."]

def name_match(user, pattern):
    return re.search(pattern, user.name(), re.IGNORECASE)

def user_list_matching_section(django_request, filter_name, filter_string, include_non_members=False):
    """Return the list of users match the given characteristic."""
    filter = user_list_filters.get(filter_name, None)
    if filter is None:
        return T.p["Filter ", filter_name, " not recognized"]
    return user_list_section(django_request, include_non_members, filter, filter_string)

def joined_before(user, datestring):
    joined, left = user.is_member()
    if not joined:
        return False
    return model.event.timestring(joined.start) < datestring

def joined_after(user, datestring):
    joined, left = user.is_member()
    if not joined:
        return False
    return model.event.timestring(joined.start) > datestring

def no_email(user, dummy):
    email = user.get_email()
    return email is None or email == ""

def no_link_id(user, dummy):
    return user.link_id == None

def no_login_name(user, dummy):
    login_name = model.database.person_get_login_name(user)
    return login_name is None or login_name == ""

def admin_note_match(user, pattern):
    note = user.get_admin_note()
    return note and re.search(pattern, note)

user_list_filters = {
    'name_matching': name_match,
    'admin_note_matching': admin_note_match,
    'date_joined_before': joined_before,
    'date_joined_after': joined_after,
    'no_email': no_email,
    'no_link_id': no_link_id,
    'no_login_name': no_login_name
}
