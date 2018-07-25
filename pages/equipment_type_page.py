from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import model.equipment_type
import model.person
import pages.page_pieces

serverconf=None

def role_people(eqty, role):
    # todo: change this to a link to the person's page instead of their email address
    return T.ul[[[T.li[T.a(href="mailto:"+who.get_email(access_permissions_role=role,
                                                        access_permissions_equipment=eqty._id))
                       [who.name(access_permissions_role=role,
                                 access_permissions_equipment=eqty._id)]]]
                 for who in sorted(eqty.get_people(role), key=model.person.Person.name)]]

def equipment_type_section(eqty, viewing_user, django_request):
    """Return a pre-HTML structure describing an equipment type."""
    global serverconf
    if serverconf == None:
        serverconf = model.configuration.get_config()['server']
    result = [T.dl[T.dt["Training category"],
                   T.dd[eqty.training_category]]]
    # todo: add admin-specific buttons
    if eqty.picture:
        result += [T.img(src=eqty.picture, align="right")]
    if eqty.manufacturer:
        result += [T.dt["Manufacturer"],
                   T.dd[eqty.manufacturer]]
    result += [T.h3["Machines"],
               [pages.page_pieces.machinelist(eqty, viewing_user, django_request, viewing_user.is_owner(eqty))]]
    roles = [("Owners", 'owner'),
             ("Trainers", 'trainer')]
    if viewing_user.is_administrator() or viewing_user.is_auditor() or viewing_user.is_owner(eqty) or viewing_user.is_trainer(eqty):
        roles.append(("Users", 'user'))
    result += [[T.h3[role_heading], # todo: make the heading a mailto link to a mailing list
                [role_people(eqty, role)]]
               for role_heading, role in roles]
    return result
