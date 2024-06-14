from tinydb import TinyDB, Query

database = TinyDB('../parameter-store.json')


def lookup_with_overrides(db, rich_text = None, series = None, topic = None):
    """Check for all stored values for a particular set of params. Start with the default values and
    override them with queries of increasing specificity based on the provided params.

    :param db (TinyDB DB or Table): database or table to look up in
    :param rich_text (bool/string/None): targeting rich text or plain text output
    :param series (string or None): name of the meetup series being populated
    :param topic (string or None): meetup topic being reused for this instance
    """
    q = Query()
    if rich_text is None:
        text_q = q
    else:
        sanitized = str(rich_text).lower()
        text_q = q.rich_text.map(lambda x: str(x).lower()) == sanitized
    if series is None:
        series_q = q
    else:
        series_q = q.meetup_series == series
    if topic is None:
        topic_q = q
    else:
        topic_q = q.topic == topic
    
    blank_q = (~q.rich_text.exists() & ~q.meetup_series.exists() & ~q.topic.exists())
    defaults = db.search(blank_q)

    for query in [text_q, series_q, topic_q]:
        merged_result = merged_query(db, query)
        defaults.update(merged_result)

    for query in [(text_q & series_q), (text_q & topic_q), (series_q & topic_q)]:
        merged_result = merged_query(db, query)
        defaults.update(merged_result)

    merged_result = merged_query(text_q & series_q & topic_q)
    defaults.update(merged_result)

    return defaults


def merged_query(db, query):
    """Query a database or table and merge all results into one

    :param db (TinyDB Database/Table): table/db to search
    :param query (TinyDB QueryInstance): search to execute
    """
    defaults = {}
    records = db.search(query)
    for r in records:
        defaults.update(r)

    return defaults
