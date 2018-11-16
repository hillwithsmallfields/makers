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
    return ", ".join(who.get_equipment_type_names(role))

def user_list_section(django_request, include_non_members=False, filter_fn=None, filter_opaque=None):
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
    # todo: must have done access_permissions.setup_access_permissions(logged_in_user) by now
    # permissions = access_permissions.get_access_permissions()
    people = person.Person.list_all_people() if include_non_members else person.Person.list_all_members()
    if filter_fn:
        people = [someone for someone in people if filter_fn(someone, filter_opaque)]
    people_dict = {whoever.name(): whoever for whoever in people}
    if permissions.auditor or permissions.admin:
        return T.table[[T.tr[T.th(class_='username')["Name"],
                             T.th(class_='user')["User"],
                             T.th(class_='owner')["Owner"],
                             T.th(class_='trainer')["Trainer"]]],
                       [T.tr[T.th(class_='username')[T.a(href=django.urls.reverse('dashboard:user_dashboard', args=([who.link_id])))[whoname]],
                             T.td(class_='user')[equipment_type_role_name_list(who, 'user')],
                             T.td(class_='owner')[equipment_type_role_name_list(who, 'owner')],
                             T.td(class_='trainer')[equipment_type_role_name_list(who, 'trainer')]]
                        for (whoname, who) in [(key, people_dict[key]) for key in sorted(people_dict.keys())]
                    ]]
    else:
        return T.p["There are "+str(len(people))
                   +(" people" if include_non_members else " members")
                   +" in the database."]

def name_match(user, pattern):
    return re.search(pattern, user.name())

def user_list_matching_section(django_request, pattern, include_non_members=False):
    """Return the list of users whose names match the given pattern."""
    return user_list_section(django_request, include_non_members, name_match, pattern)

def joined_before(user, datestring):
    joined, left = user.is_member()
    if not joined:
        return False
    return model.event.timestring(joined.start) < datestring

def user_list_before_section(django_request, datestring, include_non_members=False):
    return user_list_section(django_request, include_non_members, joined_before, datestring)

def joined_after(user, datestring):
    joined, left = user.is_member()
    if not joined:
        return False
    return model.event.timestring(joined.start) > datestring

def user_list_after_section(django_request, datestring, include_non_members=False):
    return user_list_section(django_request, include_non_members, joined_after, datestring)

user_list_filters = {
    'name': name_match,
    'before': joined_before,
    'after': joined_after
}
