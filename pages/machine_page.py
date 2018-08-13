from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.equipment_type
import model.machine
import pages.page_pieces

def machine_section(machine, django_request):
    eqty = model.equipment_type.Equipment_type.find_by_id(machine.equipment_type)
    base = django_request.scheme + "://" + django_request.META['HTTP_HOST']
    # todo: owners and admin to be able to set some details

    result = []

    # todo: picture if available

    result += [pages.page_pieces.display_or_form(
        'machine_details',
        base+"machine/update_details",
        None, ["name", "type", "description",
               "status", "status_detail",
               "location", "model", "serial_number"],
        None,
        {"name": machine.name,
         "type": eqty.name,
         "description": machine.description,
         "status": machine.status,
         "status_detail": machine.status_detail,
         "location": machine.location,
         "model": machine.model,
         "serial_number": machine.serial_number})]

    return result
