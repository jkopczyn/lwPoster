import lib.datastore

class DatastorePostingConfig:
    
    def __init__(self, file=None, secrets=None):
        self.db = lib.datastore.database
        self.secrets_db = lib.datastore.secrets_database
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
        pass

    def populate_date(self, date_obj=None):
        pass

    def get_date(self):
        pass

    def get_date_str(self):
        pass
