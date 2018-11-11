from untemplate.throw_out_your_templates_p3 import htmltags as T
import model.configuration
import model.equipment_type

serverconf=None

def equipment_type_list_section(training_category):
    global serverconf
    global org_conf
    if serverconf == None:
        serverconf = configuration.get_config('server')
    if orgconf == None:
        orgconf = configuration.get_config('organization')
    eqtys = equipment_type.Equipment_type.list_equipment_types(training_category)
    print("training_category is", training_category, "and its types are", eqtys)
    return [T.h2[(T.a(href=orgconf['categories']+training_category.upper())[training_category.capitalize()]
                  or "All") + " equipment types"],
            [T.dl[[[T.dt[T.a(href=serverconf['types']+eqty.name)[eqty.pretty_name()]],
                    T.dd[T.dl[T.dt["Machines"],
                              [T.ul(class_="compactlist")[[T.li[T.a(href=serverconf['machines']+m.name)[m.name]]
                                                                  for m in eqty.get_machines()]]],
                              T.dt["Training requests"],
                              T.dd[
                                  # todo: no training requests are visible (check whether they are even created)
                                  T.ul(class_="compactlist")[[T.li[r.name()] for r in eqty.get_training_requests('user')]]
                              ]]]]
                    for eqty in eqtys]]]]
