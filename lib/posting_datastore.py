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

