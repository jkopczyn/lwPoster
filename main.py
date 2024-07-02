import constants
import destinations.facebook
import destinations.gmail
import destinations.lesswrong
import destinations.text
import lib.helpers
import lib.pick_date
import lib.posting_config
import lib.text_generators
import text_loaders


def get_date(config):
    '''Use config to pick next date, returned as date object.

    :param config (PostingConfig) stored date about the meetup
    '''
    return lib.pick_date.next_meetup_date(config)


def post(config, topic, host, date=None, public=True, skip=None, lw_url=None):
    if skip is None:
        skip = {}

    config.include_location(host)
    config.populate_date(date) # generates from weekday_number if None
    config.populate_times()

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
            print("No destination email given, sending to sender")
            toaddr = gmail_username
        destinations.gmail.send_meetup_email(topic, config, gmail_username, toaddr)
        print("Email Sent to %s" % toaddr)
    print_plaintext = "plaintext" not in skip
    print_formatted_text = "markdown" not in skip
    if print_plaintext or print_formatted_text:
        bool_input = input("include boilerplate in text output? (y/N) ")
        b = lib.helpers.coerce_bool_input(bool_input)
    if print_plaintext:
        destinations.text.print_plaintext_meetup(topic, config, b)
    if print_formatted_text:
        destinations.text.print_text_meetup(topic, config, b)

if __name__ == "__main__":
    cfg = lib.posting_config.PostingConfig(file="config.json", secrets="secrets.json")
    topic = input("enter topic name: ")
    host = input("enter short name for location: ")
    cfg.populate_date()
    override_date = input(
            "Scheduling for %s by default. Override? (y/N) " %
            cfg.get('next_meetup_date_str')
            )
    o_d = lib.helpers.coerce_bool_input(override_date)
    if o_d:
        month = input("Provide month number (1-12): ")
        day = input("Provide day number (1-31): ")
        overridden_date = lib.pick_date.future_date(int(month), int(day))
        print("Scheduling for %s" % overridden_date.strftime(constants.long_date_format))
        cfg.populate_date(date_obj=overridden_date)
    post(cfg, topic, host, skip={
        "fb": True,
        "lw": True,
        # "discord": True,
        # "meetup": True,
        # "email": True,
        # "plaintext": True,
        # "markdown": True,
        })
