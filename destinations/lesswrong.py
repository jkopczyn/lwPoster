import datetime
import pytz
import requests
import string

from bs4 import BeautifulSoup
from getpass import getpass

import lib.text_generators


def lw2_title(topic, config):
    return lib.text_generators.gen_title(topic, config.get("meetup_name"))

def lw2_body(topic, config):
    return lib.text_generators.gen_body(topic, config)

def lw2_post_meetup(topic, config, public):
    location = config.get_default("location", {"str": ""})
    group_id = config.get("group_id")
    maps_key = config.get("maps_key")
    lw_key = config.get("lw_key")

    date_obj = config.get_date()
    startTime = datetime.time(18, 15) # make this config later
    endTime = datetime.time(21, 00) # make this config later
    with open("meetups/%s.md" % topic) as f:
        topic_text = f.read()
    return lw2_post_meetup_raw(
        lw_key,
        maps_key,
        lw2_title(topic, config),
        lw2_body(topic, config),
        location.get_default("str", ""),
        date_obj,
        startTime,
        endTime,
        group_id,
        public,
    )

def lw2_post_meetup_raw(lw_key, maps_key, title, body, location, date,
                        startTime, endTime, groupId, public):
    with open("./lib/lw2_query.graphql") as query_file:
        query = query_file.read()

    def format_time(time):
        dt = datetime.datetime.combine(date, time)
        tz = pytz.timezone("America/Los_Angeles")
        dtz = tz.localize(dt).astimezone(pytz.utc)
        return dtz.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    startTimeStr = format_time(startTime)
    endTimeStr = format_time(endTime)
    geocoding_resp = requests.get_default(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={
            "address": location,
            "key": maps_key,
        })
    googleLocation = geocoding_resp.json()["results"][0]
    mongoLocation = {
        "type":
        "Point",
        "coordinates": [
            googleLocation["geometry"]["location"]["lng"],
            googleLocation["geometry"]["location"]["lat"],
        ]
    }
    variables = {
        "document": {
            "isEvent": "true",
            "meta": False,
            "groupId": groupId,
            "location": googleLocation["formatted_address"],
            "googleLocation": googleLocation,
            "mongoLocation": mongoLocation,
            "types": ["LW", "SSC"],
            "draft": not public,
            "title": title,
            "startTime": startTimeStr,
            "endTime": endTimeStr,
            "body": body
        }
    }
    request = {
        "query": query,
        "variables": variables,
        "operationName": "createPost"
    }
    resp = requests.post(
        "https://www.lesswrong.com/graphql",
        json=request,
        headers={"authorization": lw_key},
    )
    try:
        post_id = resp.json()["data"]["createPost"]["data"]["_id"]
    except (KeyError, TypeError):
        print("Unexpected response")
        print(resp.json())
        raise
    post_url = "https://www.lesswrong.com/events/%s" % post_id
    return post_url


def delete_lw2_post(postId, lw_key):
    unPost = string.Template("""
mutation {
    PostsRemove(documentId: "$_id"){
        _id
    }
}
""")
    resp = requests.post(
        "https://www.lesserwrong.com/graphql",
        json={'query': unPost.substitute(_id=postId)},
        headers={"authorization": lw_key},
    )
    j = resp.json()
    print(j)


def lw_login(username, password=None):
    url = "http://lesswrong.com/post/login"

    password = password or getpass("LW password: ")

    payload = {
        "rem": "on",
        "user_login": username,
        "op": "login-main",
        "passwd_login": password,
    }

    response = requests.request(
        "POST", url, data=payload, allow_redirects=False)

    if "reddit_session" not in response.cookies:
        raise LookupError("Login Failed")

    return response.cookies


def lw_get_uh(cookies):
    url = "http://lesswrong.com/meetups/new/"

    response = requests.request("Get", url, cookies=cookies)
    response_html = BeautifulSoup(response.text, "html.parser")
    return response_html.find("input", attrs={"name": "uh"})["value"]
