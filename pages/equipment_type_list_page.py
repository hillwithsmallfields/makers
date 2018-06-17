from nevow import tags as T
import equipment_type

def equipment_type_list_section(training_category):
    eqtys = equipment_type.Equipment_type.list_equipment_types(training_category)
    print "training_category is", training_category, "and its types are", eqtys
    return [T.h2[(training_category or "all").capitalize() + " equipment types"],
            [T.dl[[[T.dt[eqty.pretty_name()],
                   T.dd[T.dl[
                       T.dt["Machines"], [str(m_id) # todo: linkified machine name
                                           for m_id in eqty.get_machines()]
                       # todo: status
                       # todo: location
                       # todo: owners, trainers, users, as allowed by context
                       # todo: any other information
                    ]]] for eqty in eqtys]]]]
