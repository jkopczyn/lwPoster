import string

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
