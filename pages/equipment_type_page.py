from nevow import tags as T
import configuration
import equipment_type
import person

serverconf=None

def role_people(eqty, role):
    return T.ul[[[T.li[T.a(href="mailto:"+who.get_email(access_permissions_role=role,
                                                        access_permissions_equipment=eqty._id))
                       [who.name(access_permissions_role=role,
                                 access_permissions_equipment=eqty._id)]]]
                 for who in sorted(eqty.get_people(role), key=person.Person.name)]]

def eqty_machines(eqty):
    return T.dl[[[T.dt[T.a(href=serverconf['machines']+m.name)[m.name]],
                  T.dd[T.dl[T.dt["Status"], T.dd[m.status or "Unknown"],
                            T.dt["Location"], T.dd[m.location or "Unknown"],
                            T.dt["Serial number"], T.dd[m.serial_number or "Unknown"]]]]
                 for m in eqty.get_machines()]]

def equipment_type_section(eqty):
    """Return a pre-HTML structure describing an equipment type."""
    global serverconf
    if serverconf == None:
        serverconf = configuration.get_config()['server']
    result = [T.dl[T.dt["Training category"],
                   T.dd[eqty.training_category]]]
    # todo: add admin-specific buttons
    if eqty.manufacturer:
        result += [T.dt["Manufacturer"],
                   T.dd[eqty.manufacturer]]
    result += [T.dt["Machines"],
               T.dd[eqty_machines(eqty)]]
    result += [[T.dt[role_heading],
                T.dd[role_people(eqty, role)]]
               for role_heading, role in [("Owners", 'owner'),
                                          ("Trainers", 'trainer'),
                                          ("Users", 'user')]]
    return result
