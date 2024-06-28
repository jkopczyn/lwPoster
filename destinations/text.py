import lib.pick_date
import text_loaders


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
