Using the development server
============================

Copying files around
--------------------

From my development machine, if I don't want to check a version in to
github, I can send it across with scripts/ctts (Copy To Test Server).

This puts them into the project directory within my home directory.

Putting the files into the service location
-------------------------------------------

Once the files are in my project directory, I can put them into the
live directory with scripts/install-makers.sh, which also moves files
between the subdirectories a bit, and runs scripts/setpassword which
isn't checked into github, as one of the config files which does have
a password written into it is checked in; the checked-in version just
has a placeholder.

Running the system
------------------

Eventually it will run automatically, but for now
scripts/gunicorn_start.sh will start it manually.
