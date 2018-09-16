import csv
import model.database
import model.equipment_type
import subprocess
import tempfile

def export_equipment_types(filename):
    pass

def export_machines(filename):
    pass

def export_members(filename):
    pass

def export_users(filename):
    with open(filename, "w") as outfile:
        users_writer = csv.writer(outfile)
        users_writer.writerow(["Equipment", "Name", "Date", "Trainer"])
        for eqty in equipment_type.Equipment_type.list_equipment_types():
            eqname = eqty.name
            for user in eqty.get_trained_users():
                users_writer.writerow([eqname, user.name()
                                       # todo: add date and trainer
                                   ])

def export_owners(filename):
    pass

def export_trainers(filename):
    pass

def export_templates(filename):
    pass

def export_all(backup_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        export_equipment_types(os.path.join(tmpdir, "equipment_types.csv"))
        export_machines(os.path.join(tmpdir, "machines.csv"))
        export_members(os.path.join(tmpdir, "members.csv"))
        export_users(os.path.join(tmpdir, "users.csv"))
        export_owners(os.path.join(tmpdir, "owners.csv"))
        export_trainers(os.path.join(tmpdir, "trainers.csv"))
        export_templates(os.path.join(tmpdir, "templates.csv"))
        subprocess.run(["tar", "czf", backup_file] + glob.glob(os.path.join(tmpdir, "*.csv")))
