#!/usr/bin/python

import sys
sys.path.append('common')
sys.path.append('pages')

from nevow import flat
from nevow import tags as T
import database
import pages

def main():
    config = config.get_config()
    person = database.get_person('John Sturdy')
    test_content = [pages.test_page_section("Landing page",
                                            pages.landing_page_content(person))]
    print pages.page_string("Test page", test_content)

if __name__ == "__main__":
    main()
