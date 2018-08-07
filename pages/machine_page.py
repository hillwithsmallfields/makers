from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.equipment_type
import model.machine

def machine_section(machine):
    eqty = model.equipment_type.Equipment_type.find_by_id(machine.equipment_type)
    # todo: owners and admin to be able to set some details
    rows = [T.tr[T.th(class_='ralabel')["Name"], T.td[machine.name]],
            T.tr[T.th(class_='ralabel')["Type"], T.td[T.a()[eqty.name]]]]
    # todo: any logged-in user to be able to make status reports
    if machine.description:
        rows += [T.tr[T.th(class_='ralabel')["Description"], T.td[machine.description]]]
    rows += [T.tr[T.th(class_='ralabel')["Status"], T.td[machine.status]]]
    result = [T.table[rows]]
    return result
