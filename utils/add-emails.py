#!/usr/bin/env python

from __future__ import print_function

import csv
sys.path.append('model')
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from model.person import Person

def add_emails_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action='store_true')
    parser.add_argument("file")
    args = parser.parse_args()
    force = args.force
    with open(args.file) as csvfile:
        for row in csv.DictReader(csvfile):
            if 'Name' not in row or 'Email' not in row:
                continue
            name = row['Name']
            email = row['Email']
            whoever = Person.find(name)
            if whoever is None:
                print("Could not find", name)
                continue
            old_email = whoever.get_email()
            old_not_valid = old_email is None or old_email.startswith("member_") or old_email == ""
            if force or old_not_valid:
                whoever.set_email(email)
                if old_not_valid:
                    print("Set email for", name, "to", email)
                else:
                    print("Changed email for", name, "to", email, "from", old_email)

if __name__ == "__main__":
    add_emails_main()
