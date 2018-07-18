from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import model.equipment_type
import model.machine

serverconf=None

def machine_section(machine):
    global serverconf
    if serverconf == None:
        serverconf = model.configuration.get_config()['server']
    eqty = model.equipment_type.Equipment_type.find_by_id(machine.equipment_type)
    result = [T.table[T.tr[T.th["Name"], T.td[machine.name]],
                      T.tr[T.th["Type"], T.td[T.a()[eqty.name]]],
                      T.tr[T.th["Status"], T.td[machine.status]]]]
    return result
