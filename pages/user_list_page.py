from nevow import tags as T
import access_permissions
import configuration
import person

serverconf=None

def user_list_section(include_non_members=False):
    global serverconf
    if serverconf == None:
        serverconf = configuration.get_config()['server']
    # todo: must have done access_permissions.setup_access_permissions(logged_in_user) by now
    permissions = access_permissions.get_access_permissions()
    people = person.Person.list_all_people() if include_non_members else person.Person.list_all_members()
    if permissions.auditor or permissions.admin:
        return T.ul[[T.li[who.name] for who in people]]
    else:
        return T.p["There are "+str(len(people))
                   +(" people" if include_non_members else " members")
                   +" in the database."]
