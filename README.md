# makers
This is a membership, equipment and training database for maker
spaces.

It was written to unify a database for membership with managing
training sessions and equipment status.

The context for which it was written is an organization with members
and equipment, which requires the members to be trained on the
equipment before they are allowed to use it.  There are three
relationships which users can have with equipment:

 - user
 - owner (maintainer)
 - trainer

# Installation and setup

scripts/install-system.sh will install most of the prerequisites, and
scripts/install-makers.sh will install the makers system.  These
scripts currently assume a debian-family system (the development
platform was Raspbian).

# Structure and technology

Accounts, login and sessions are handled by django, but we don't use
its templates; all the views are produced with view functions, using
an "untemplate" system.  Django keeps a very basic user account
database, extending its base account class with a "link_id" which is a
UUID used in that account and the corresponding accounts in the
databases holding the main information.

Apart from django's user account database, there are two mongodb
collections holding information about users: an "operational database"
which holds the core practical information about each user (but not
human-oriented stuff like their names), and a "profile database" which
contains their names, contact details, interests etc.  These are
separate so that we can delete all the personally identifying
information about someone (as required by the GDPR) without breaking
the operational information which may need to retain a reference
(anonymously if necessary) to that person.

There are also mongodb collections for equipment types, individual
machines, and events (both planned and historical).

The main motives for developing the system were to organize training
on equipment types, and to keep a record of who is trained on what.

Event collection entries are created to allow users to sign up to the
events, and are retained permanently as a record of who has been
trained on what.  A person is "user" of an equipment type if they have
successfully attended a user training session on it; an "owner" of it
if they have successfully attended an owner training session, and a
"trainer" if they have successfully attended a trainer training
session.

# Special equipment categories

Membership of the organization is represented by being trained on a
type of "equipment" which represents the organization itself, and
database system adminstrator status is represented by being trained on
a type of "equipment" which is the database system itself.

# Code structure

The top-level django setup is in the directory "makers", and the
django apps under it are in the directory "apps".

The page-generating code is in "pages", and the underlying logic is in
"model".  Most of the mongodb access is done in model/database.py.

"config" contains a YAML file setting the organization name, database
collection names, etc, and the CSS files styling the pages, and a
little javascript for tabbed pages.
