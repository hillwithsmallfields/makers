from nevow import flat
from nevow import tags as T

def person_page_contents(who, viewer):
    return [T.h2["Personal details"],
            T.div(_class="personaldetails")[
                # todo: address etc to go here
                ],
            T.h2["Availability"],
            T.div(_class="availability")[
                # todo: availability table to go here
                ],
            T.h2["Equipment responsibilities"],
            T.div(_class="responsibilities")[
                # todo: owner / trainer table to go here
                ],
            T.h2["Equipment trained on"],
            T.div(_class="trainedon")[
                # todo: list of equipment trained on to go here
                ]
            T.h2["Training requests"],
            T.div(_class="requested")[
                # todo: list of outstanding training requests to go here
                ]
            T.h2["Events I'm hosting"],
            T.div(_class="hostingevents")[
                # todo: list of events they're hosting to go here
                ],
            T.h2["Events signed up for"],
            T.div(_class="signedevents")[
                # todo: list of events signed up for to go here
                ],
            T.h2["Events I can sign up for"],
            T.div(_class+"availableevents")[
                # todo: list of available events to go here
                ],
            T.h2["API links"],
            T.div(_class="apilinks")[
                # todo: api links to go here
                ]]
