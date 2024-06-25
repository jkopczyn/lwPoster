import json

class PostingConfig:
    public = {}
    secret = {}

    def __init__(self, file="config.json", secrets="secrets.json"):
        self.public = json.load(open(file))
        self.secret = json.load(open(secrets))

    @classmethod
    def from_dict(cls, d):
        c = cls()
        c.public = dict()
        c.secret = d
        return c

    def get(self, *args):
        if len(args) < 1:
            raise KeyError
        if len(args) == 1:
            return self.secret.get(args[0], self.public.get(args[0]))
        tmp_p = self.public
        tmp_s = self.secret
        for key in args:
            tmp_s = tmp_s.get(key, {})
            tmp_p = tmp_p.get(key, {})
        if tmp_s and tmp_s != {}:
            return tmp_s
        if tmp_p and tmp_p != {}:
            return tmp_p
        raise KeyError

    def set(self, *args):
        if len(args) < 2:
            raise KeyError
        if len(args) == 2:
            self.public[args[0]] = args[1]
        k = {}
        v = {}
        for key in args:
            k = v
            v = key
        self.public[k] = v

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

default_config = PostingConfig()

def config(file, secrets):
    return PostingConfig(file, secrets)
