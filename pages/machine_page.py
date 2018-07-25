from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.equipment_type
import model.machine

def machine_section(machine):
    eqty = model.equipment_type.Equipment_type.find_by_id(machine.equipment_type)
    # todo: owners and admin to be able to set some details
    result = [T.table[T.tr[T.th["Name"], T.td[machine.name]],
                      T.tr[T.th["Type"], T.td[T.a()[eqty.name]]],
                      # todo: any logged-in user to be able to make status reports
                      T.tr[T.th["Status"], T.td[machine.status]]]]
    return result
