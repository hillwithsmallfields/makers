from nevow import flat
from nevow import tags as T

import database
import pages

def list_equipment_content():
    return []

def list_equipment_page():
    return pages.page_string("Equipment list",
                             list_equipment_content())
