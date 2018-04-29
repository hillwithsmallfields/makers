#!/usr/bin/env python
# -*- coding: utf8

import sys
sys.path.append('common')

import csv, random, datetime, configuration

surnames = ["Bernard", "Brown", "Clarke", "Davies", "Dubois", "Evans",
            # "Kamiński", "Müller", "Wiśniewski", "Wójcik", # with accented characters
            "Fischer", "Green", "Hall", "Jackson", "Johnson", "Jones",
            "Kelmendi", "Kowalczyk", "Kowalski", "Lewandowski",
            "Maes", "Maler", "Martin", "Meyer", "Nowak", "Roberts",
            "Robinson", "Schmidt", "Schneider", "Smith", "Altdorf",
            "Martin", "Earl", "StClair", "Farquhar", "Levi", "Albrecht",
            "Neumann", "Johansson", "Jansson", "Svensson", "Carey",
            "Armstrong", "Lejeune", "Young", "Jung", "Taylor", "Green",
            "Hinton", "Bond", "Farmer", "Palmer", "Thompson", "Virtanen",
            "Wagner", "Walker", "White", "Williams", "Wilson",
            "Wood", "Wright"]

forenames = ["Alexandru", "Alice", "Andrei", "Anna", "Charlie", "Charlotte",
             # "Chloé", "Inès", "Léa", # with accented characters
             "David", "Emma", "Gabriel", "George", "Harry",
             "Jack", "Jacob", "John", "Louise", "Noah", "Oliver",
             "Timothy", "Tina", "Tania", "Gavin", "Roger", "Ivan",
             "Carlos", "Ewan", "Eoin", "Caomhghin", "Donncha",
             "Oscar", "Sarah", "Thomas", "Anthony", "Christine", "Antonia",
             "Mark", "Judith", "Daniel", "Adam", "Catherine", "Silvia",
             "Quentin", "Robert", "Rupert", "Gwendoline", "Amanda",
             "Miranda", "Jan", "Janet", "Susan"]

animals = ["Fox", "Mongoose", "Lizard", "Bat", "Mouse", "Raptor"]

furniture = [ "Accubita", "Bar", "Bean", "Bed", "Bench", "Bunk", "Canapé",
              "Canopy", "Chair", "Chaise", "Couch", "Davenport", "Daybed",
              "Divan", "Fainting", "Fauteuil", "Footstool", "Four-poster",
              "Futon", "Hammock", "Headboard", "Klinai", "Lift", "Mattress",
              "Multiple", "Murphy", "Ottoman", "Platform", "Recliner",
              "Rocking", "Sleigh", "Sofa", "Stool", "Tuffet", "Waterbed" ]

emailers = ["gmail", "hotmail", "yahoo"]

member_fields = ['Member no',
                 'Name',
                 'Email',
                 'Inductor',
                 'Date inducted',
                 'Exit-only fob issued?',
                 'Code',
                 'Code returned?',
                 'Fob enabled & e-mail sent on',
                 'Enabled by',
                 'Date expired',
                 'Fob disabled on (date)',
                 'Fob disabled by (name)']

trained_fields = ['Equipment', 'Name', 'Date', 'Trainer']

owners_fields = ['Equipment', 'Name', 'Date']

trainers_fields = ['Equipment', 'Name', 'Date']

def main():
    by_email = {}
    by_number = {}
    by_name = {}
    inductor = "Joe Bloggs"
    inductors = []
    induction_date = datetime.date(2013,03,19)
    induction_size = random.randrange(1, 6)
    config = configuration.get_config()
    equipment_classes = {}
    with open('equipment-types.csv') as types_file:
        for row in csv.DictReader(types_file):
            equipment_classes[row['name']] = row
    equipment_last_training_sessions = {}
    equipment_last_trainers = {}
    del equipment_classes['makespace']
    # record training only for red equipment
    equipment_classes = [ eqcl for eqcl in equipment_classes.keys()
                          if equipment_classes[eqcl].get('training_category', 'red') == 'red' ]
    users = {}
    owners = {}
    trainers = {}
    member_no = 1
    while member_no < 1010:
        if member_no == 1:
            forename = "Joe"
            surname = "Bloggs"
        else:
            forename = random.choice(forenames)
            surname = random.choice(surnames)
        name = forename + " " + surname
        if name in by_name:
            print "duplicate name", name, member_no
            continue
        print "unique name", name, member_no
        member_no += 1
        e1 = forename.lower()
        e2 = surname.lower()
        email = random.choice([e1, e1[0:1]]) + random.choice(["", ".", "_"]) + e2 + "@" + random.choice(emailers) + ".com"
        induction_size -= 1
        if induction_size == 0:
            induction_size = random.randrange(1, 6)
            inductor = random.choice(inductors) if len(inductors) > 0 else "Joe Bloggs" # the first member must be their own inductor
            induction_date = induction_date + datetime.timedelta(random.randrange(3,7))
        if email not in by_email: # avoid duplicates
            row = {'Member no': member_no,
                   'Name': name,
                   'Email': email,
                   'Inductor': inductor,
                   'Date inducted': induction_date.isoformat(),
                   'Exit-only fob issued?': 'Yes',
                   'Code': random.choice(animals)+random.choice(furniture),
                   'Code returned?': "Yes",
                   'Fob enabled & e-mail sent on': induction_date+datetime.timedelta(random.randrange(1,4)),
                   'Enabled by': random.choice(inductors) if len(inductors) > 0 else inductor
            }
            # decreasing probability that they've left
            if random.randrange(member_no) < 24:
                row['Date expired'] = induction_date+datetime.timedelta(random.randrange(90,700))
            trained_on = {}
            for ec in equipment_classes:
                if random.random() < 0.2: # 0.2 of all users trained on each device
                    if ec not in equipment_last_training_sessions or random.random() < 0.25: # bunch the trainees for that equipment
                        training_date = (induction_date + datetime.timedelta(random.randrange(14,90))).isoformat()
                        trainer = random.choice(trainers[ec])['Name'] if ec in trainers else "unknown trainer"
                        equipment_last_training_sessions[ec] = training_date
                        equipment_last_trainers[ec] = trainer
                    else:
                        training_date = equipment_last_training_sessions[ec]
                        trainer = equipment_last_trainers[ec]
                    tr = {'Equipment': ec,
                          'Name': name,
                          'Date': training_date,
                          'Trainer': trainer}
                    trained_on[ec] = tr
                    users[ec] = users.get(ec,[]) + [tr]
                    if random.random() < 0.1:
                        owners[ec] = owners.get(ec, []) + [{'Equipment': ec,
                                                            'Name': name,
                                                            'Date': (induction_date + datetime.timedelta(random.randrange(14,90))).isoformat()}]
                    if random.random() < 0.1:
                        trainers[ec] = trainers.get(ec, []) + [{'Equipment': ec,
                                                                'Name': name,
                                                                'Date': (induction_date + datetime.timedelta(random.randrange(14,90))).isoformat()}]
            row['trained_on'] = trained_on
            by_email[email] = row
            by_number[member_no] = row
            by_name[name] = row
            if member_no < 4 or random.random() < 0.01:
                inductors = inductors + [name]
    max_member_number = member_no
    with open("members.csv", "w") as member_file:
        member_writer = csv.DictWriter(member_file,
                                       fieldnames=member_fields,
                                       extrasaction='ignore')
        member_writer.writeheader()
        for member_no in range(0, max_member_number):
            if member_no in by_number:
                member_writer.writerow(by_number[member_no])
    with open("users.csv", "w") as trained_file:
        trained_writer = csv.DictWriter(trained_file, fieldnames=trained_fields)
        trained_writer.writeheader()
        for eusers in users.values():
            for euser in eusers:
                trained_writer.writerow(euser)
    with open("owners.csv", 'w') as owners_file:
        owners_writer = csv.DictWriter(owners_file, fieldnames=owners_fields)
        owners_writer.writeheader()
        for equipment, owners in owners.iteritems():
            for owner in owners:
                owners_writer.writerow(owner)
    with open("trainers.csv", 'w') as trainers_file:
        trainers_writer = csv.DictWriter(trainers_file, fieldnames=trainers_fields)
        trainers_writer.writeheader()
        for equipment, trainers in trainers.iteritems():
            for trainer in trainers:
                trainers_writer.writerow(trainer)

if __name__ == "__main__":
    main()
