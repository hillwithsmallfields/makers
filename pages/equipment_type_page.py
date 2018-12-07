from untemplate.throw_out_your_templates_p3 import htmltags as T
import django.urls
import model.configuration
import model.equipment_type
import model.person
import pages.event_page
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

    conf = model.configuration.get_config()

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
                      conf['organization']['categories']+eqty.training_category),
         'description': eqty.description,
         'manufacturer': eqty.manufacturer})]

    result += [T.h3["Machines"],
               [pages.page_pieces.machinelist(eqty, viewing_user, django_request, viewing_user.is_owner(eqty))]]
    if not viewing_user.is_trained(eqty):
        result += [T.h3["User training"],
                   pages.event_page.event_table_section(eqty.get_training_events('user',
                                                                                 earliest=model.times.now()),
                                                        viewing_user._id, django_request)]
    else:
        if not viewing_user.is_owner(eqty):
            result += [T.h3["Owner training"],
                       pages.event_page.event_table_section(eqty.get_training_events('owner',
                                                                                     earliest=model.times.now()),
                                                            viewing_user._id, django_request)]
        if not viewing_user.is_trainer(eqty):
            result += [T.h3["Trainer training"],
                       pages.event_page.event_table_section(eqty.get_training_events('trainer',
                                                                                     earliest=model.times.now()),
                                                            viewing_user._id, django_request)]
    roles = []
    if viewing_user.is_trainer(eqty):
        result += [T.h3["Training requests"],
                   pages.page_pieces.eqty_training_requests(eqty, django_request)]
        roles += [("Owners", 'owner'),
                 ("Trainers", 'trainer')]
    if (viewing_user.is_administrator()
        or viewing_user.is_auditor()
        or viewing_user.is_owner(eqty)
        or viewing_user.is_trainer(eqty)):
        roles.append(("Users", 'user'))
        result += [[T.h3[T.a(href=("mailto:"+eqty.name+"_"+role+"s@"
                                   +conf['server']['mailhost']))[role_heading]],
                    [role_people(eqty, role)]]
               for role_heading, role in roles]
    return result
