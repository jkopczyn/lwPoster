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

    def get(self, *list_of_keys):
        # this doesn't really work on the same API

    def get_default(self, *args):
        if len(args) < 2:
            raise KeyError
        default = args[-1]
        args = args[:-1]
        try:
            v = self.get(*args)
            if v != None:
                return v
        except KeyError:
            pass
        v = default
        self.set(*args, v)
        return v


