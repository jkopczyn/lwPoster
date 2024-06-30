import constants
import lib.pick_date
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
            raise TypeError('no args to a get call')
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
        # if more than two, nest them in successive dicts
        # or I think that's what this is supposed to do
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

    def include_location(self, host):
        loc_dict = self.get("locations")
        loc_props = loc_dict.get(host)
        if loc_props is None:
            raise ValueError('no location for host %s' % host)
        self.set("location", loc_props)

    def populate_date(self, date_obj=None):
        if date_obj is None and self.get_date() is None:
            date_obj = lib.pick_date.next_meetup_date(self)
        date_str = date_obj.strftime(constants.date_format)
        self.set('next_meetup_date', date_obj)
        self.set('next_meetup_date_str', date_str)

    def get_date(self):
        return self.get('next_meetup_date')

    def get_date_str(self):
        return self.get('next_meetup_date_str')


default_config = PostingConfig()

def config(file, secrets):
    return PostingConfig(file, secrets)
