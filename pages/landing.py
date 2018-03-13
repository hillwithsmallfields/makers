#!/usr/bin/python

import sys
sys.path.append('../common')

from nevow import flat
from nevow import tags as T
import config
import database

def trained_descr(devclass):
    return [T.h3[devclass['class']],
            T.p["Trained by " + devclass['trained by'],
                " on ", devclass['since']]]

def owning_descr(device):
    return T.h3[device['machine']]

def trainer_descr(devclass):
    return T.h3[devclass['class']]

def landing_page(person):
    name = person['given_name'] + " " + person['family_name']
    trained = [ [trained_descr(devclass) for devclass in person['trained']] ]
    if len(trained) > 0:
        trained = [ T.h2["Trained"]] + trained
    owning = [ [owning_descr(equipment) for equipment in person['owner']] ]
    if len(owning) > 0:
        owning = [ T.h2["Owner"]] + owning
    trainer = [ [trainer_descr(devclass) for devclass in person['trainer']] ]
    if len(trainer) > 0:
        trainer = [ T.h2["Trainer"]] + trainer
    page = T.html[T.head[T.title["Home for " + name]],
                  T.body[T.h1["Home for " + name],
                         T.h2["Events registered for"],
                         T.p[T.a(href="person_profile")["View/edit profile"]],
                         trained,
                         owning,
                         trainer]]
    return flat.flatten(page)

def main():                     # for testing
    john = database.get_person('John Sturdy')
    print landing_page(john)

if __name__ == "__main__":
    main()
