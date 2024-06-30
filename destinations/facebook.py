import datetime
import requests

from bs4 import BeautifulSoup
from getpass import getpass

import lib.text_generators

def fb_login(email, password=None):
    url = "https://m.facebook.com/login.php"

    password = password or getpass("FB password: ")

    payload = {
        "email": email,
        "pass": password,
    }

    response = requests.request(
        "POST", url, data=payload, allow_redirects=False)

    if "c_user" not in response.cookies:
        raise LookupError("Login Failed")

    return response.cookies


def fb_get_dstg(cookies):
    url = "https://m.facebook.com/events/create/basic"
    response = requests.request("Get", url, cookies=cookies)
    response_html = BeautifulSoup(response.text, "html.parser")
    return response_html.find("input", attrs={"name": "fb_dtsg"})["value"]


def fb_post(fb_cookies,
            fb_dstg,
            title,
            description,
            location,
            date,
            time,
            public=False):
    url = "https://www.facebook.com/ajax/create/event/submit"

    url_encoded_payload = {
        "title": title,
        "description": description,
        "location": location,
        "location_id": "null_%s" % location,
        "cover_focus[x]": "0.5",
        "cover_focus[y]": "0.5",
        "only_admins_can_post": "false",
        "post_approval_required": "false",
        "start_date": date.strftime("%D"),
        "start_time": time.hour * 3600 + time.minute * 60 + time.second,
        #"end_date": "3/28/2017",
        #"end_time": "72000",
        "timezone": "America/Los_Angeles",
        #"acontext": r'{"sid_create":"1763740711","action_history":"[{\"surface\":\"create_dialog\",\"mechanism\":\"user_create_dialog\",\"extra_data\":[]}]","has_source":true}',
        "acontext": "{}",
        "event_ent_type": 1 + public,
        "guests_can_invite_friends": "true",
        "guest_list_enabled": "true",
        "save_as_draft": "false",
        "friend_birthday_prompt_xout_id": "",
        "is_multi_instance": "false",
        "dpr": "1",
    }
    form_data_payload = {
        "fb_dtsg": fb_dstg,
    }

    return requests.request(
        "POST",
        url,
        params=url_encoded_payload,
        data=form_data_payload,
        cookies=fb_cookies,
        allow_redirects=False)

def fb_title(topic, config):
    meetup_name = config.get_default("fb_meetup_name", "")
    if meetup_name == "":
        meetup_name = config.get("meetup_name")
    return lib.text_generators.gen_title(topic, meetup_name)

def fb_email(config):
    fb_login_email = config.get_default("fb_login_email", "")
    if fb_login_email == "":
        fb_login_email = config.get("email")
    return fb_login_email

def fb_pass(config):
    return config.get_default("fb_login_password", None)

def fb_body(topic, config):
    return lib.text_generators.gen_body(topic, config)

def fb_meetup_attrs(topic, config):
    date_obj = config.get_date()
    time = datetime.time(18, 15) # make this config later
    location = config.get("location")
    return (
        fb_email(config), fb_title(topic, config), fb_body(topic, config),
        location, date_obj, time
    )

def fb_post_meetup(topic, config, public=False):
    fb_email, title, description, location, date, time = fb_meetup_attrs(topic, config)
    fb_password = fb_pass(config)
    fb_cookies = fb_login(fb_email, fb_password)
    fb_dstg = fb_get_dstg(fb_cookies)
    res = fb_post(
        fb_cookies,
        fb_dstg,
        title=title,
        description=description,
        location=location.get("str"),
        date=date,
        time=time,
        public=public)
    if not res.ok:
        raise requests.HTTPError(res)
