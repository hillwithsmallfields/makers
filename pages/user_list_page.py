from untemplate.throw_out_your_templates_p3 import htmltags as T

import model.access_permissions as access_permissions
import model.configuration as configuration
import model.person as person

serverconf=None

def user_list_section(include_non_members=False, filter_fn=None):
    """Return the users list, if the viewing person is allowed to see it.
    Otherwise, just how many people there are.
    The optional first argument is a flag for whether to include non-members.
    The optional second argument is a boolean function taking a person object,
    returning whether to include them in the list.  This could be used for things
    like listing people whose fobs are ready for enabling, or who have missed
    paying their latest subscription."""
    global serverconf
    if serverconf == None:
        serverconf = configuration.get_config()['server']
    users_base = serverconf['base_url']+serverconf['users']
    # todo: must have done access_permissions.setup_access_permissions(logged_in_user) by now
    # permissions = access_permissions.get_access_permissions()
    people = person.Person.list_all_people() if include_non_members else person.Person.list_all_members()
    if filter_fn:
        people = [someone for someone in people if filter_fn(someone)]
    if True: # permissions.auditor or permissions.admin:
        return T.ul[[T.li[T.a(href=users_base+who.link_id)[who.name()]] for who in people]]
    else:
        return T.p["There are "+str(len(people))
                   +(" people" if include_non_members else " members")
                   +" in the database."]
