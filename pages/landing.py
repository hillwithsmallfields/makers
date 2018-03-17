from nevow import flat
from nevow import tags as T

import database
import pages

def relation_table(person, role):
    return [T.table[ [ T.tr[T.th[devclass['class']],
                            T.td[devclass['trained by']],
                            T.td[devclass['since']]]
                      for devclass in sorted(set([ machine['class']
                                        for machine in get_person_machines(person, role) ])) ] ] ]

def landing_page_content(person):
    trained = relation_table(person, 'trained')
    if len(trained) > 0:
        trained = [T.h2["Trained"]] + trained
    owning = relation_table(person, 'owner')
    if len(owning) > 0:
        owning = [T.h2["Owner"]] + owning
    trainer = relation_table(person, 'trainer')
    if len(trainer) > 0:
        trainer = [T.h2["Trainer"]] + trainer
    return [T.h2["Events registered for"],
                            T.p[T.a(href="person_profile")["View/edit profile"]],
                            trained,
                            owning,
                            trainer]

def landing_page(person):
    name = person['given_name'] + " " + person['family_name']
    return pages.page_string("Home for " + name,
                             landing_page_content(person))

def main():                     # for testing
    print landing_page(john)

if __name__ == "__main__":
    main()
