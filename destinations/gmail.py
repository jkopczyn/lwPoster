import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass

import lib.text_generators
import text_loaders

def email_pieces(topic, config):
    boilerplate = text_loaders.load_boilerplate(config)
    topic_title = text_loaders.load_text_title(topic)
    topic_text, topic_plaintext = text_loaders.load_text_and_plaintext_body(topic)
    location = config.get("location")
    when_str = lib.text_generators.gen_time_range(
            config.get('start_time_obj'),
            config.get('end_time_obj')
            )
    plain_email = lib.text_generators.gen_message_plaintext(when_str, location.get("str"), topic_plaintext, boilerplate)
    html_email = lib.text_generators.gen_message_html(when_str, location.get("str"), topic_text, boilerplate)
    email_title = _email_title(topic, config)
    return (email_title, plain_email, html_email)

def _email_title(topic, config):
    return lib.text_generators.gen_title_with_date(
            topic,
            config.get("meetup_name"),
            config.get_date_str())

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
