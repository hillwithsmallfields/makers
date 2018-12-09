import csv
import model.equipment_type
import model.times
import os
import subprocess

def make_database_backup(tarballfilename=None):
    """Make a backup in tarball, and return its filename."""
    with tempfile.TemporaryDirectory() as dirname:
        backupname = "backup-"+model.times.timestring(model.times.now())
        innerdirname = os.path.join(dirname, backupname)
        if tarballfilename is None:
            tarballfilename = os.path.join(dirname, backupname+".tgz")
        for role in ['user', 'owner', 'trainer']:
            eqtys = model.equipment_type.Equipment_type.list_equipment_types()
            rows = []
            for eqty in eqtys:
                rows += eqty.backup_API_people(role)
            with open(os.path.join(innerdirname, role+"s.csv"), 'w') as csv_stream:
                writer = csv.DictWriter(role_stream,
                                        ['Equipment', 'Name', 'Date', 'Trainer'],
                                        extrasaction='ignore')
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)

        subprocess.run(["tar",
                        "cfz", tarballfilename,
                        "--directory", dirname,
                        backupname])

        return tarballfilename
