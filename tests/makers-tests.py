#!/usr/bin/env python

import sys
sys.path.append('common')
sys.path.append('pages')
sys.path.append('/home/jcgs/open-projects/nevow/nevow')

# print "sys.path is now", sys.path

from nevow import flat
from nevow import tags as T
import configuration
import database
import equipment_class
import landing
import list_equipment
import list_members
import pages
import timeslots

def main():
    config = configuration.get_config()
    database.database_init(config)
    person = database.get_person_dict('Joe Bloggs')
    test_content = [pages.test_page_section("List of members",
                                            list_members.list_members(person))
                    ,
                    pages.test_page_section("Landing page",
                                            landing.landing_page_content(person))
                    # ,
                    # pages.test_page_section("Timeslots",
                    #                         timeslots.timeslots_form(configuration.get_config(), 12345))
                    # ,
                    # pages.test_page_section("Equipment list",
                    #                         list_equipment.list_equipment_content())
                    # ,
                    # pages.test_page_section("Equipment class page",
                    #                         equipment_class.equipment_class_content("laser_cutter"))
    ]
    print(pages.page_string("Test page", test_content))

if __name__ == "__main__":
    main()
