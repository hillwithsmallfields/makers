from untemplate.throw_out_your_templates_p3 import htmltags as T

import model.access_permissions as access_permissions
import model.configuration as configuration
import model.person as person
import model.event
import re

serverconf=None

def user_list_section(django_request, include_non_members=False, filter_fn=None, filter_opaque=None):
    """Return the users list, if the viewing person is allowed to see it.
    Otherwise, just how many people there are.
    The optional first argument is a flag for whether to include non-members.
    The optional second argument is a boolean function taking a person object,
    returning whether to include them in the list.  This could be used for things
    like listing people whose fobs are ready for enabling, or who have missed
    paying their latest subscription.  A third argument is passed through
    to that function."""
    if not include_non_members: # debug hack
        print("members list for debugging", person.Person.list_all_members()) # debug hack
    include_non_members = True  # debug hack
    global serverconf
    if serverconf == None:
        serverconf = configuration.get_config()['server']
    users_base = django_request.scheme + "://" + django_request.META['HTTP_HOST'] + serverconf['users']
    # todo: must have done access_permissions.setup_access_permissions(logged_in_user) by now
    # permissions = access_permissions.get_access_permissions()
    people = person.Person.list_all_people() if include_non_members else person.Person.list_all_members()
    print("raw list", people)
    if filter_fn:
        people = [someone for someone in people if filter_fn(someone, filter_opaque)]
        print("filtered list", people)
    people_dict = {whoever.name(): whoever for whoever in people}
    # todo: remove this dirty hack which I put in for early testing
    if True: # permissions.auditor or permissions.admin:
        return T.table[[T.tr[T.th["Name"], T.th["User"], T.th["Owner"], T.th["Trainer"]]],
                       [T.tr[T.th[T.a(href=users_base+who.link_id)[whoname]],
                             T.td[", ".join(who.get_equipment_type_names('user'))],
                             T.td[", ".join(who.get_equipment_type_names('owner'))],
                             T.td[", ".join(who.get_equipment_type_names('trainer'))]]
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
