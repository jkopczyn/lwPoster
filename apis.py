import datetime
import json
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass

import destinations.facebook
import destinations.lesswrong
import lib.helpers
import lib.pick_date
import lib.posting_config
import lib.text_generators
import text_loaders

def email_pieces(topic, config):
    boilerplate = text_loaders.load_boilerplate(config)
    topic_title = text_loaders.load_text_title(topic)
    topic_text, topic_plaintext = text_loaders.load_text_and_plaintext_body(topic)
    date = lib.pick_date.next_meetup_date(config)
    location = config.get("location")
    when_str = lib.text_generators.gen_time(18, 15) # make this config later
    plain_email = lib.text_generators.gen_message_plaintext(when_str, location.get("str"), topic_plaintext, boilerplate)
    html_email = lib.text_generators.gen_message_html(when_str, location.get("str"), topic_text, boilerplate)
    email_title = _email_title(topic, config, date)
    return (email_title, plain_email, html_email)

def _email_title(topic, config, date_obj):
    return lib.text_generators.gen_title_with_date(
            topic, config.get("meetup_name"), date_obj.strftime("%b %d"))

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
        boilerplate = text_loaders.load_boilerplate(config)
    topic_title = text_loaders.load_text_title(topic)
    meetup_name = config.get("meetup_name")
    date_obj = lib.pick_date.next_meetup_date(config)
    date_str = date_obj.strftime("%B %d")
    location = config.get("location")
    loc_str = location.get("str")
    time_str = "%s - %s" % (
            lib.text_generators.gen_time(18, 15),
            lib.text_generators.gen_time(22, 00)
            ) # make this config later
    description = lib.text_generators.gen_markdown_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate)
    print(description)
    with open("description.txt", 'w') as f:
        f.write(description)


def print_plaintext_meetup(topic, config, use_boilerplate):
    boilerplate = ""
    if use_boilerplate:
        boilerplate = text_loaders.load_boilerplate(config)
    topic_title = text_loaders.load_text_title(topic)
    meetup_name = config.get("meetup_name")
    date_obj = lib.pick_date.next_meetup_date(config)
    date_str = date_obj.strftime("%B %d")
    location = config.get("location")
    loc_str = location.get("str")
    time_str = "%s - %s" % (
            lib.text_generators.gen_time(18, 15),
            lib.text_generators.gen_time(22, 00)
            ) # make this config later
    description = lib.text_generators.gen_plaintext_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate)
    print(description)
    with open("plaindescription.txt", 'w') as f:
        f.write(description)



# from subprocess import Popen, PIPE
# # what was this for? printing to a file instead of dual-printing?
# def print_command(command, **kwargs):
#     print(" ".join(command))
#     p = Popen(command, stdout=PIPE, stderr=PIPE, **kwargs)
#     output, err = p.communicate()
#     print(output, end=' ')
#     if err:
#         print(err, end=' ')
#     if p.returncode != 0:
#         raise IOError("Return Status %i" % p.returncode)


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
            toaddr = gmail_username
        send_meetup_email(topic, config, gmail_username, toaddr)
        print("Email Sent to %s" % toaddr)
    print_plaintext = "plaintext" not in skip
    print_formatted_text = "markdown" not in skip
    if print_plaintext or print_formatted_text:
        bool_input = input("include boilerplate in text output? (y/N) ")
        b = lib.helpers.coerce_bool_input(bool_input)
    if print_plaintext:
        print_plaintext_meetup(topic, config, b)
    if print_formatted_text:
        print_text_meetup(topic, config, b)

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
