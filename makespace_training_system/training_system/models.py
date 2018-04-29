from django.db import models


# Base class for auditing
class BaseModel:
    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)


#######################################################################################################################
# Entities for lists and config options
#
######################################################################################################################

# The type of dietary options, Vegetarian, Vegan, Kosher, Halal, etc
class DietaryOption(BaseModel, models.Model):
    name = models.CharField(max_length=32, blank=False)


#######################################################################################################################
#  Main entities
#
######################################################################################################################
class EquipmentType(BaseModel, models.Model):
    TRAINING_CAT_OPTIONS = [
        ('G', 'Green'),
        ('A', 'Amber'),
        ('R', 'Red')
    ]

    name = models.CharField(max_length=128, blank=False, null=False)
    category = models.CharField(max_length=4, choices=TRAINING_CAT_OPTIONS, default='G')

    def __str__(self):
        return self.name


class Equipment(BaseModel, models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


# FIXME: This needs to be a separate database for GDPR
class PersonDetails(BaseModel, models.Model):
    given_name = models.CharField(max_length=128, blank=False, null=False, default='')
    surname = models.CharField(max_length=128, blank=False, null=False, default='')
    known_as = models.CharField(max_length=128, blank=True, null=False, default='')
    email = models.CharField(max_length=256, blank=False, null=False, default='')

    # TODO: Need to have proper postal adress field: First line, town/city/ post code
    postal_address = models.CharField(max_length=256, blank=False, null=False, default='')

    photo_url = models.CharField(max_length=256, blank=True, null=True, default='')
    hide_photo = models.BooleanField(default=True)

    # A boolean (flag) field for whether people want status changes to be announced on the “announcements” part of the
    # system, so they can have their Name and Interests fields made into an announcement when they join, and perhaps
    # have “... is now trained on…”, “... is now an owner of …” etc announced too.
    announce_changes = models.BooleanField(default=False)

    # A free-text field in which people can enter a description of what they’re interested in, if they’re prepared to
    # have that information shared
    interests = models.TextField(max_length=2048, blank=True, null=False, default='')

    # For those who are members; possibly a temporary number, distinguished by
    # being negative, to track them through the joining process
    membership_number = models.CharField(max_length=64, blank=True, null=False, default='')

    # Display person's name
    def __str__(self):
        return "%s %s (%s)" % (self.surname, self.given_name, self.known_as)


# Member door access control key fob
class Fob(BaseModel, models.Model):
    number = models.CharField(max_length=32, blank=True, null=False)
    active = models.BooleanField(default=False)
    assigned = models.BooleanField(default=False)

    def __str__(self):
        active_msg = "active" if self.active else "not active"
        assigned_msg = "assigned" if self.active else "not assigned"
        return "%s is %s and %s" % (self.number, assigned_msg, active_msg)


class FobLog(BaseModel, models.Model):
    pass


# This is the main entity for interacting with a member
class Member(BaseModel, models.Model):
    # Not usable as a permanent identifier, as people sometime lose fobs and get replacements; might be done as a list
    # of fob numbers issued so we have some record of the fob loss/damage/replacement rate
    fob_number = models.ForeignKey(Fob, on_delete=models.SET_NULL, null=True)

    box_issued = models.DateField()

    dietary_requirement = models.ForeignKey(DietaryOption, on_delete=models.SET_NULL, null=True)



