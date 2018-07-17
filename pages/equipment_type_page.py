from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import model.equipment_type
import model.person

serverconf=None

def role_people(eqty, role):
    # todo: change this to a link to the person's page instead of their email address
    return T.ul[[[T.li[T.a(href="mailto:"+who.get_email(access_permissions_role=role,
                                                        access_permissions_equipment=eqty._id))
                       [who.name(access_permissions_role=role,
                                 access_permissions_equipment=eqty._id)]]]
                 for who in sorted(eqty.get_people(role), key=model.person.Person.name)]]

def eqty_machines(eqty):
    # todo: put making links such as machine names into a function, then later make it use django's mechanism for getting app names
    return T.dl[[[T.dt[T.a(href=serverconf['machines']+m.name)[m.name]],
                  T.dd[T.dl[T.dt["Status"], T.dd[m.status or "Unknown"],
                            T.dt["Location"], T.dd[m.location or "Unknown"],
                            T.dt["Serial number"], T.dd[m.serial_number or "Unknown"]]]]
                 for m in eqty.get_machines()]]

def equipment_type_section(eqty):
    """Return a pre-HTML structure describing an equipment type."""
    global serverconf
    if serverconf == None:
        serverconf = model.configuration.get_config()['server']
    result = [T.dl[T.dt["Training category"],
                   T.dd[eqty.training_category]]]
    # todo: add admin-specific buttons
    if eqty.manufacturer:
        result += [T.dt["Manufacturer"],
                   T.dd[eqty.manufacturer]]
    result += [T.dt["Machines"],
               T.dd[eqty_machines(eqty)]]
    result += [[T.dt[role_heading], # todo: make the heading a mailto link to a mailing list
                T.dd[role_people(eqty, role)]]
               for role_heading, role in [("Owners", 'owner'),
                                          ("Trainers", 'trainer'),
                                          # todo: make the users list visible only to owners, trainers, admins, auditors
                                          ("Users", 'user')]]
    return result
