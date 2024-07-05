import constants
import lib.datastore

class DatastorePostingConfig:
    
    def __init__(self, file=None, secrets=None):
        self.db = lib.datastore.database
        self.secrets_db = lib.datastore.secrets_database
        self.scheduled_date = None
        if file is not None:
            self.db = lib.datastore.open_db(file)
        if secrets is not None:
            self.secrets_db = lib.datastore.open_db(secrets)


    @classmethod
    def from_dict(cls, d):
        raise TypeError("Datastore can't be initialized from dict")

    def get_location(self, lookup_params):
        # directly from a host
        in_table =  lib.datastore.inputs_from_db(self.db)
        loc_table =  lib.datastore.locations_from_db(self.db)
        entry = datastore.lookup_with_overrides(in_table, lookup_params)
        loc_name = entry['location']
        return lib.datastore.lookup_with_overrides(
                loc_table, {'location': loc_name})


    def populate_times(self):
        start = self.get_default('start_time', constants.default_start_time)
        end = self.get_default('end_time', constants.default_end_time)
        self.start_time =lib.helpers.process_time_str(start)
        self.end_time = lib.helpers.process_time_str(end)

    def populate_date(self, date_obj=None):
        if date_obj is None:
            date_obj = self.get_date()
        if date_obj is not None:
            return
        date_obj = lib.pick_date.next_meetup_date(self)
        self.scheduled_date = date_obj
        self.scheduled_date_str = date_obj.strftime(constants.date_format)

    def get_date(self):
        return self.scheduled_date

    def get_date_str(self):
        return self.scheduled_date_str
