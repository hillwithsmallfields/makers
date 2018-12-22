import csv
import model.equipment_type
import model.person
import model.times
import os
import subprocess
import tempfile

def make_database_backup(tarballfilename=None,
                         callback=None):
    """Make a backup in a tarball.

    A callback can be given, to be applied to the filename; if this is
    used, its result is the returned by this function.

    If no callback is given, the filename is returned.

    If you don't give a filename, a temporary file will be used, the
    name of which is given to the callback as its only argument, and
    which will disappear after the callback returns.

    If you do give a filename, it is passed through
    datetime.datetime.strftime() using the current time, so, for
    example, you could give "/var/backup/makers-%A.tgz" to have a
    filename based on day of the week, for re-use of files after a
    week."""

    with tempfile.TemporaryDirectory() as dirname:
        backupname = "backup-"+model.times.timestring(model.times.now())
        innerdirname = os.path.join(dirname, backupname)
        if tarballfilename is None:
            tarballfilename = model.times.format_now(os.path.join(dirname, backupname+".tgz"))
        os.makedirs(innerdirname)
        for role in ['user', 'owner', 'trainer']:
            eqtys = model.equipment_type.Equipment_type.list_equipment_types()
            rows = []
            for eqty in eqtys:
                rows += eqty.backup_API_people(role)
            csvname = os.path.join(innerdirname, role+"s.csv")
            with open(csvname, 'w') as csv_stream:
                writer = csv.DictWriter(csv_stream,
                                        ['Equipment', 'Name', 'Date', 'Trainer'],
                                        extrasaction='ignore')
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
        with open(os.path.join(innerdirname, "members.csv"), 'w') as csv_stream:
            writer = csv.DictWriter(csv_stream,
                                    ['Member no','Name','Email'],
                                    extrasaction='ignore')
            writer.writeheader()
            for whoever in model.person.Person.list_all_members():
                writer.writerow({'Member no': str(whoever.membership_number),
                                 'Name': whoever.name(),
                                 'Email': whoever.get_email()})

        with open(os.path.join(innerdirname, "equipment_types.csv"), 'w') as csv_stream:
            writer = csv.DictWriter(csv_stream,
                                    ['name',
                                     'presentation_name',
                                     'description',
                                     'training_category',
                                     'manufacturer'],
                                    extrasaction='ignore')
            writer.writeheader()
            for eqty in model.equipment_type.Equipment_type.list_equipment_types():
                rowdict = {'name': eqty.name,
                           'training_category': eqty.training_category,
                           'manufacturer': eqty.manufacturer}
                if eqty.presentation_name:
                    rowdict['presentation_name'] = eqty.presentation_name
                if eqty.description:
                    rowdict['description'] = eqty.description
                writer.writerow(rowdict)

        with open(os.path.join(innerdirname, "equipment.csv"), 'w') as csv_stream:
            writer = csv.DictWriter(csv_stream,
                                    ['name', 'equipment_type', 'location',
                                     'description', 'status',
                                     'brand', 'model', 'serial_number'],
                                    extrasaction='ignore')
            writer.writeheader()
            for eqty in model.equipment_type.Equipment_type.list_equipment_types():
                for machine in eqty.get_machines():
                    rowdict = {'name': machine.name,
                               'equipment_type': machine.equipment_type,
                               'location': machine.location}
                    if machine.description:
                        rowdict['description'] = machine.description
                    if machine.status:
                        rowdict['status'] = machine.status
                    if machine.brand:
                        rowdict['brand'] = machine.brand
                    if machine.model:
                        rowdict['model'] = machine.model
                    if machine.serial_number:
                        rowdict['serial_number'] = machine.serial_number
                    writer.writerow(rowdict)

        subprocess.run(["tar",
                        "cfz", tarballfilename,
                        "--directory", dirname,
                        backupname])

        if callback:
            return callback(tarballfilename)

        return tarballfilename
