import lib.datastore

class DatastorePostingConfig:
    
    def __init__(self, file=None, secrets=None):
        if file is None:
            self.db = lib.datastore.database
        else:
            self.db = lib.datastore.open_db(file)
        if secrets is None:
            self.secrets_db = lib.datastore.secrets_database
        else:
            self.secrets_db = lib.datastore.open_db(secrets)


    @classmethod
    def from_dict(cls, d):
        raise TypeError("Datastore can't be initialized from dict")

