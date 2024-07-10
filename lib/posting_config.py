import constants
import datetime
import lib.pick_date
import json

class PostingConfig:
    public = {}
    secret = {}

    def __init__(self, file="config.json", secrets="secrets.json"):
        self.public = json.load(open(file))
        self.secret = json.load(open(secrets))

    @classmethod
    def from_dict(cls, d): # used for tests only
        c = cls()
        c.public = dict()
        c.secret = d
        return c

    def get(self, key):
        return self.secret.get(key, self.public.get(key))

    def set(self, *args):
        if len(args) < 2:
            raise KeyError
        if len(args) == 2:
            self.public[args[0]] = args[1]
        # if more than two, nest them in successive dicts
        # or I think that's what this is supposed to do
        # I suspect I tested this and that was the only time it ever went past two args
        k = {}
        v = {}
        for key in args:
            k = v
            v = key
        self.public[k] = v

    def get_default(self, key, default_value):
        ret = self.get(key)
        if ret is None:
            self.set([key], default_value)
            return default_value
        return ret

    def include_location(self, host):
        loc_dict = self.get("locations")
        loc_props = loc_dict.get(host)
        if loc_props is None:
            raise ValueError('no location for host %s' % host)
        self.set("location", loc_props)

    def populate_date(self, date_obj=None):
        if date_obj is None:
            date_obj = self.get_date()
        if date_obj is None:
            date_obj = lib.pick_date.next_meetup_date(self)
        date_str = date_obj.strftime(constants.date_format)
        self.set('next_meetup_date', date_obj)
        self.set('next_meetup_date_str', date_str)

    def populate_times(self):
        start = self.get_default('start_time', constants.default_start_time)
        end = self.get_default('end_time', constants.default_end_time)
        self.set('start_time_obj', lib.helpers.process_time_str(start))
        self.set('end_time_obj', lib.helpers.process_time_str(end))

    def get_date(self):
        return self.get('next_meetup_date')

    def get_date_str(self):
        return self.get('next_meetup_date_str')


default_config = PostingConfig()

def config(file, secrets):
    return PostingConfig(file, secrets)
