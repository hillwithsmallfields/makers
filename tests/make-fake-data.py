#!/usr/bin/env python
# -*- coding: utf8

import sys
sys.path.append('common')

import csv, random, datetime, configuration

surnames = ["Bernard", "Brown", "Clarke", "Davies", "Dubois", "Evans",
            "Fischer", "Green", "Hall", "Jackson", "Johnson", "Jones",
            "Kamiński", "Kelmendi", "Kowalczyk", "Kowalski", "Lewandowski",
            "Maes", "Maler", "Martin", "Meyer", "Müller", "Nowak", "Roberts",
            "Robinson", "Schmidt", "Schneider", "Smith", "Surname",
            "Svensson", "Taylor", "Thompson", "Virtanen", "Wagner", "Walker",
            "White", "Williams", "Wilson", "Wiśniewski", "Wood", "Wright",
            "Wójcik"]

forenames = ["Alexandru", "Alice", "Andrei", "Anna", "Charlie", "Charlotte",
             "Chloé", "David", "Emma", "Gabriel", "George", "Harry", "Inès",
             "Jack", "Jacob", "John", "Louise", "Léa", "Noah", "Oliver",
             "Oscar", "Sarah", "Thomas",]

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
    inductor = "Self"
    inductors = []
    induction_date = datetime.date(2013,03,19)
    induction_size = random.randrange(1, 6)
    config = configuration.get_config()
    equipment_classes = config['equipment_classes']
    equipment_last_training_sessions = {}
    equipment_last_trainers = {}
    del equipment_classes['makespace']
    equipment_classes = [ eqcl for eqcl in equipment_classes.keys()
                          if equipment_classes[eqcl].get('training_class', 'red') == 'red' ]
    users = {}
    owners = {}
    trainers = {}
    for member_no in range(1,1010):
        if member_no == 1:
            forename = "Joe"
            surname = "Bloggs"
        else:
            forename = random.choice(forenames)
            surname = random.choice(surnames)
        name = forename + " " + surname
        e1 = forename.lower()
        e2 = surname.lower()
        email = random.choice([e1, e1[0:1]]) + random.choice(["", ".", "_"]) + e2 + "@" + random.choice(emailers) + ".com"
        induction_size -= 1
        if induction_size == 0:
            induction_size = random.randrange(1, 6)
            inductor = random.choice(inductors) if len(inductors) > 0 else "Self"
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
                   'Enabled by': random.choice(inductors) if len(inductors) > 0 else "Self"
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
            if member_no < 4 or random.random() < 0.01:
                inductors = inductors + [name]
    with open("members.csv", "w") as member_file:
        member_writer = csv.DictWriter(member_file,
                                       fieldnames=member_fields,
                                       extrasaction='ignore')
        member_writer.writeheader()
        for member_no in range(1010,0,-1):
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
