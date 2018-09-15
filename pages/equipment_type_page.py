from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.configuration
import model.equipment_type
import model.person
import pages.page_pieces

def role_people(eqty, role):
    # todo: change this to a link to the person's page instead of their email address
    return T.ul[[[T.li[T.a(href="mailto:"+who.get_email(access_permissions_role=role,
                                                        access_permissions_equipment=eqty._id))
                       [who.name(access_permissions_role=role,
                                 access_permissions_equipment=eqty._id)]]]
                 for who in sorted(eqty.get_people(role), key=model.person.Person.name)]]

def equipment_type_section(eqty, viewing_user, django_request):
    """Return a pre-HTML structure describing an equipment type."""

    result = []

    if eqty.picture:
        result += [T.img(src=eqty.picture, align="right")]

    result += [pages.page_pieces.display_or_form(
        'equipment_type_details',
        django.urls.reverse('equiptypes:update_details'),
        None,
        ['category', 'description', 'manufacturer'],
        None,
        {'category': (eqty.training_category,
                      model.configuration.get_config()['organization']['categories']+eqty.training_category),
         'description': eqty.description,
         'manufacturer': eqty.manufacturer})]

    result += [T.h3["Machines"],
               [pages.page_pieces.machinelist(eqty, viewing_user, django_request, viewing_user.is_owner(eqty))]]
    # todo: add list of upcoming training events, using eqty.get_training_events(role, earliest=times.event.now())
    # todo: add lists of training requests, using eqty.get_training_requests(role, django_request); may be able to use eqty_training_requests from person_page.py
    if viewing_user.is_trainer(eqty):
        result += [T.h3["Training requests"],
                   pages.page_pieces.eqty_training_requests(eqty, django_request)]
    roles = [("Owners", 'owner'),
             ("Trainers", 'trainer')]
    if viewing_user.is_administrator() or viewing_user.is_auditor() or viewing_user.is_owner(eqty) or viewing_user.is_trainer(eqty):
        roles.append(("Users", 'user'))
    result += [[T.h3[role_heading], # todo: make the heading a mailto link to a mailing list
                [role_people(eqty, role)]]
               for role_heading, role in roles]
    return result
