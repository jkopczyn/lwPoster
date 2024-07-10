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
        self.cache = {}


    def get_cache(self):
        return self.cache

    def get(self, key):
        return self.cache.get(key)


    def input_lookup(self, org_keys):
        cache = lib.datastore.lookup_with_overrides(
                self.input_table, org_keys)
        self.cache |= cache
        if 'location' in cache:
            loc_cache = self.get_location(cache['location'])
            cache |= loc_cache
        return cache


    def output_lookup(self, org_keys):
        cache = lib.datastore.lookup_with_overrides(
                self.output_table, org_keys)
        self.cache |= cache
        return cache


    def secret_lookup(self, org_keys):
        cache = lib.datastore.lookup_with_overrides(
                self.secrets_db, org_keys)
        self.cache |= cache
        if 'location' in cache:
            loc_cache = self.get_location(cache['location'])
            cache |= loc_cache
        return cache


    def get_location(self, loc_name):
        loc_data = lib.datastore.lookup_with_overrides(
                self.locations_table, {'location': loc_name})
        self.cache |= loc_data
        return loc_data


    def populate_times(self):
        start = self.cache.get('start_time', constants.default_start_time)
        end = self.cache.get('end_time', constants.default_end_time)
        self.start_time = lib.helpers.process_time_str(start)
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
