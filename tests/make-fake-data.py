#!/usr/bin/python
# -*- coding: utf8

import csv, random, datetime

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

def main():
    with open("members.csv", "w") as member_file:
        member_writer = csv.DictWriter(member_file, fieldnames=member_fields)
        member_writer.writeheader()
        by_email = {}
        by_number = {}
        inductor = "Self"
        inductors = []
        induction_date = datetime.date(2013,03,19)
        induction_size = random.randrange(1, 6)
        for member_no in range(1,1010):
            forename = random.choice(forenames)
            surname = random.choice(surnames)
            name = forename + " " + surname
            email = forename.lower() + surname.lower() + "@" + random.choice(emailers) + ".com"
            induction_size -= 1
            if induction_size == 0:
                induction_size = random.randrange(1, 6)
                inductor = random.choice(inductors)
                induction_date = induction_date + datetime.timedelta(random.randrange(3,7))
            if email not in by_email:
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
                by_email[email] = row
                by_number[member_no] = row
                if member_no < 4 or random.random() < 0.01:
                    inductors = inductors + [name]
        for member_no in range(1010,0,-1):
            if member_no in by_number:
                member_writer.writerow(by_number[member_no])

if __name__ == "__main__":
    main()
