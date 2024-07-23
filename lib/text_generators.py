import datetime
import markdown

import text_loaders

def gen_body(topic, config):
    boilerplate = text_loaders.load_boilerplate(config)
    topic_text, _ = text_loaders.load_text_and_plaintext_body(topic)
    return "%s\n%s" % (topic_text, boilerplate)

def gen_title(topic, meetup_name):
    topic_title = text_loaders.load_text_title(topic).strip()
    return "%s: %s" % (meetup_name, topic_title)

def gen_title_with_date(topic, meetup_name, date_str):
    topic_title = text_loaders.load_text_title(topic).strip()
    return "%s: %s: Wednesday %s" % (meetup_name, date_str, topic_title)

def gen_time(hour24, minute):
    return gen_time_from_obj(datetime.time(hour24, minute))

def gen_time_from_obj(datetime_obj):
    return datetime_obj.strftime('%l:%M %p')

def gen_time_range(start_obj, end_obj):
    return "%s - %s" % (gen_time_from_obj(start_obj), gen_time_from_obj(end_obj))


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

def gen_message_plaintext(time_str, loc_str, topic_text, boilerplate):
    if boilerplate == "":
        return _plaintext_template_no_boilerplate % (time_str, loc_str, topic_text)
    return _plaintext_template % (time_str, loc_str, topic_text, boilerplate)

def gen_message_markdown(time_str, loc_str, topic_text, boilerplate):
    if boilerplate == "":
        return _markdown_template_no_boilerplate % (time_str, loc_str, topic_text)
    return _markdown_template % (time_str, loc_str, topic_text, boilerplate)

def gen_message_html(time_str, loc_str, topic_text, boilerplate):
    return markdown.markdown(gen_message_markdown(time_str, loc_str, topic_text, boilerplate))

def gen_plaintext_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate):
    _, topic_plaintext = text_loaders.load_text_and_plaintext_body(topic)
    return "%s\n%s" % (gen_title_with_date(topic, meetup_name, date_str),
            gen_message_plaintext(time_str, loc_str, topic_plaintext, boilerplate))

def gen_markdown_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate):
    topic_text, _ = text_loaders.load_text_and_plaintext_body(topic)
    return "__%s__\n\n%s" % (gen_title_with_date(topic, meetup_name, date_str),
            gen_message_markdown(time_str, loc_str, topic_text, boilerplate))

def gen_html_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate):
    return markdown.markdown(gen_markdown_with_title(topic, meetup_name, date_str, time_str, loc_str, boilerplate))
