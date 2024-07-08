import constants
import lib.datastore

class DatastorePostingConfig:
    
    def __init__(self):
        self.db = lib.datastore.database
        self.input_table = lib.datastore.input_values_table
        self.output_table = lib.datastore.output_forms_table
        self.locations_table = lib.datastore.locations_table
        self.secrets_db = lib.datastore.secrets_database
        self.scheduled_date = None
        self.cache = None

    def lookup(self, org_keys):
        cache = lib.datastore.lookup_with_overrides(self.db, org_keys)
        if self.cache:
            self.cache |= cache
        return self.cache

    def secret_lookup(self, org_keys):
        cache = lib.datastore.lookup_with_overrides(
                self.secrets_db, org_keys)
        if self.cache:
            self.cache |= cache
        return self.cache

    def get_location(self, lookup_params):
        # directly from a host
        entry = datastore.lookup_with_overrides(self.input_table, lookup_params)
        loc_name = entry['location']
        loc_data = lib.datastore.lookup_with_overrides(
                self.locations_table, {'location': loc_name})
        self.cache |= loc_data
        return loc_data


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
