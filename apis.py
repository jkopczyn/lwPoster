import smtplib
from getpass import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import datetime
import markdown
import json
import string
import urllib.request, urllib.parse, urllib.error
from subprocess import Popen, PIPE

import destinations.lesswrong
import destinations.facebook
import lib.posting_config
import lib.pick_date


def load_boilerplate(config):
    phone = config.get("phone")
    location_config = config.get("location")
    boilerplate_path = config.get_default("boilerplate_path", "boilerplate.md")
    if "phone" in location_config:
        phone = "%s (general meetup info at %s)" % (location_config.get("phone"),
                                                    phone)
    if "instructions" in location_config:
        instructions = location_config.get("instructions") + "\n"
    else:
        instructions = ""
    with open(boilerplate_path) as f:
        boilerplate = string.Template(instructions + f.read())
    return boilerplate.substitute(phone=phone)

def load_text_title(topic):
    with open("meetups/title/%s.md" % topic) as f:
        topic_title = f.read()
    return topic_title

def load_text_and_plaintext_body(topic):
    with open("meetups/body/%s.md" % topic) as f:
        topic_text = f.read()
    try:
        with open("meetups/plainbody/%s.md" % topic) as f:
            topic_plaintext = f.read()
    except IOError:
        topic_plaintext = topic_text
    return (topic_text, topic_plaintext)

def gen_body(topic, config):
    boilerplate = load_boilerplate(config)
    topic_text, _ = load_text_and_plaintext_body(topic)
    return "%s\n%s" % (topic_text, boilerplate)

def gen_plaintext_body(topic, config):
    boilerplate = load_boilerplate(config)
    _, topic_plaintext = load_text_and_plaintext_body(topic)
    return "%s\n%s" % (topic_plaintext, boilerplate)

def gen_title(topic, meetup_name):
    topic_title = load_text_title(topic).strip()
    return "%s: %s" % (meetup_name, topic_title)

def gen_title_with_date(topic, meetup_name, date_str):
    topic_title = load_text_title(topic).strip()
    return "%s: %s: %s" % (meetup_name, date_str, topic_title)

def gen_time(hour24, minute):
    x = datetime.time(hour24, minute)
    return x.strftime('%l:%M %p')

_plaintext_template_no_boilerplate = """WHEN: %s
WHERE: %s

%s"""
_plaintext_template = """WHEN: %s
WHERE: %s

%s
%s"""
_markdown_template_no_boilerplate = """**WHEN:** %s
**WHERE:** %s

%s"""
_markdown_template = """**WHEN:** %s
**WHERE:** %s

%s
%s"""

def message_plaintext(time_str, loc_str, topic_text, boilerplate):
    if boilerplate == "":
        return _plaintext_template_no_boilerplate % (time_str, loc_str, topic_text)
    return _plaintext_template % (time_str, loc_str, topic_text, boilerplate)

def message_markdown(time_str, loc_str, topic_text, boilerplate):
    if boilerplate == "":
        return _markdown_template_no_boilerplate % (time_str, loc_str, topic_text)
    return _markdown_template % (time_str, loc_str, topic_text, boilerplate)

def message_html(time_str, loc_str, topic_text, boilerplate):
    return markdown.markdown(message_markdown(time_str, loc_str, topic_text, boilerplate))

def plaintext_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate):
    _, topic_plaintext = load_text_and_plaintext_body(topic)
    return "%s\n%s" % (gen_title_with_date(topic, meetup_name, date_str),
            message_plaintext(time_str, loc_str, topic_plaintext, boilerplate))

def markdown_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate):
    topic_text, _ = load_text_and_plaintext_body(topic)
    return "__%s__\n\n%s" % (gen_title_with_date(topic, meetup_name, date_str),
            message_markdown(time_str, loc_str, topic_text, boilerplate))

def html_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate):
    return markdown.markdown(markdown_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate))




def email_pieces(topic, config):
    boilerplate = load_boilerplate(config)
    topic_title = load_text_title(topic)
    topic_text, topic_plaintext = load_text_and_plaintext_body(topic)
    date = lib.pick_date.next_meetup_date(config)
    location = config.get("location")
    when_str = gen_time(18, 15) # make this config later
    plain_email = message_plaintext(when_str, location.get("str"), topic_plaintext, boilerplate)
    html_email = message_html(when_str, location.get("str"), topic_text, boilerplate)
    email_title = _email_title(topic, config, date)
    return (email_title, plain_email, html_email)

def _email_title(topic, config, date_obj):
    return gen_title_with_date(topic, config.get("meetup_name"), date_obj.strftime("%b %d"))

def send_meetup_email(topic, config, gmail_username, toaddr):
    email_title, plaintext_email, html_email = email_pieces(topic, config)
    msg = MIMEMultipart("alternative")

    fromaddr = "%s@gmail.com" % gmail_username
    msg["Subject"] = email_title
    msg["From"] = fromaddr
    msg["To"] = toaddr

    part1 = MIMEText(plaintext_email, "plain")
    msg.attach(part1)
    part2 = MIMEText(html_email, "html")
    msg.attach(part2)

    gmail = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    pwd = config.get("gmail_app_password")
    if not pwd:
        pwd = getpass("Gmail application-specific password: ")
    gmail.login(gmail_username, pwd)
    gmail.sendmail(fromaddr, toaddr, msg.as_string())




def print_text_meetup(topic, config, use_boilerplate):
    boilerplate = ""
    if use_boilerplate:
        boilerplate = load_boilerplate(config)
    topic_title = load_text_title(topic)
    meetup_name = config.get("meetup_name")
    date_obj = lib.pick_date.next_meetup_date(config)
    date_str = date_obj.strftime("%B %d")
    location = config.get("location")
    loc_str = location.get("str")
    time_str = "%s - %s" % (gen_time(18, 15), gen_time(22, 00)) # make this config later
    description = markdown_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate)
    print(description)
    with open("description.txt", 'w') as f:
        f.write(description)


def print_plaintext_meetup(topic, config, use_boilerplate):
    boilerplate = ""
    if use_boilerplate:
        boilerplate = load_boilerplate(config)
    topic_title = load_text_title(topic)
    meetup_name = config.get("meetup_name")
    date_obj = lib.pick_date.next_meetup_date(config)
    date_str = date_obj.strftime("%B %d")
    location = config.get("location")
    loc_str = location.get("str")
    time_str = "%s - %s" % (gen_time(18, 15), gen_time(22, 00)) # make this config later
    description = plaintext_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate)
    print(description)
    with open("plaindescription.txt", 'w') as f:
        f.write(description)




def print_command(command, **kwargs):
    print(" ".join(command))
    p = Popen(command, stdout=PIPE, stderr=PIPE, **kwargs)
    output, err = p.communicate()
    print(output, end=' ')
    if err:
        print(err, end=' ')
    if p.returncode != 0:
        raise IOError("Return Status %i" % p.returncode)


def post(config, topic, host, public=True, skip=None, lw_url=None):
    if skip is None:
        skip = {}
    config.set("location", config.get("locations").get(host))
    # Facebook disabled until further notice
    # looks like it's no longer possible to post as a user
    # you must register as an app and get group owner permission to post with that app
    # if "fb" not in skip:
    #     destinations.facebook.fb_post_meetup(topic, config, public)
    #     print("Posted to Facebook")
    if "lw" not in skip:
        lw_url = destinations.lesswrong.lw2_post_meetup(topic, config, public)
        print(lw_url)
    if "email" not in skip:
        gmail_username = config.get("gmail_username")
        if public:
            email_group = config.get("email_group")
            toaddr = email_group
        else:
            toaddr = "%s@gmail.com" % gmail_username
        send_meetup_email(topic, config, gmail_username, toaddr)
        print("Email Sent")
    print_plaintext = "plaintext" not in skip
    print_formatted_text = "markdown" not in skip
    if print_plaintext or print_formatted_text:
        boil_input = input("include boilerplate? (y/N) ")
        coerced_boil = boil_input.strip().lower()
        if coerced_boil == "y" or coerced_boil == "yes":
            boil = True
        elif coerced_boil == "n" or coerced_boil == "no" or coerced_boil == "":
            boil = False
        else:
            print("Didn't understand response, defaulting to no boilerplate")
            boil = False
    if print_plaintext:
        print_text_meetup(topic, config, boil)
    if print_formatted_text:
        print_plaintext_meetup(topic, config, boil)

if __name__ == "__main__":
    cfg = lib.posting_config.PostingConfig(file="config.json", secrets="secrets.json")
    topic = input("enter topic name: ")
    host = input("enter short name for location: ")
    post(cfg, topic, host, skip={
        "fb": True,
        "lw": True,
        # "discord": True,
        # "meetup": True,
        # "email": True,
        # "plaintext": True,
        # "markdown": True,
        })
