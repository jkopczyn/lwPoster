from tinydb import TinyDB, Query

# database = TinyDB('../parameter-store.json')

organizational_keys = ["rich_text", "meetup_series", "topic"]
q = Query()

def lookup_with_overrides(db, rich_text = None, series = None, topic = None):
    """Check for all stored values for a particular set of params. Start with the default values and
    override them with queries of increasing specificity based on the provided params.

    :param db (TinyDB DB or Table): database or table to look up in
    :param rich_text (bool/string/None): targeting rich text or plain text output
    :param series (string or None): name of the meetup series being populated
    :param topic (string or None): meetup topic being reused for this instance
    """
    keys_to_queries = {key: ~(q[key].exists()) for key in organizational_keys}

    if rich_text is not None:
        sanitized = str(rich_text).lower()
        text_q = q.rich_text.map(lambda x: str(x).lower()) == sanitized
        keys_to_queries["rich_text"] = text_q
    if series is not None:
        keys_to_queries["meetup_series"] = q.meetup_series == series
    if topic is not None:
        keys_to_queries["topic"] = q.topic == topic

    blank_q = blanks_query([])
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


def intersect_queries(queries):
    if len(queries) == 0:
        return Query()
    q = queries[0]
    idx = 1
    while idx < len(queries):
        q = q & queries[idx]
        idx += 1
    return q

def query_plus_organizational_blanks(query, nonblank_keys):
    return blanks_query(nonblank_keys, query)


def merged_query(db, query):
    """Query a database or table and merge all results into one

    :param db (TinyDB DB or Table): database or table to look up in
    :param query (TinyDB QueryInstance): search to execute
    """
    defaults = {}
    records = db.search(query)
    for r in records:
        defaults.update(r)

    return defaults


def blanks_query(nonblank_keys, initial_query=None):
    if initial_query == None:
        initial_query = ~q.DO_NOT_USE.exists()

    blanks_q = initial_query
    for k in organizational_keys:
        if k in nonblank_keys:
            continue
        blanks_q = blanks_q & ~(q[k].exists())
    return blanks_q


def interactive_insert_data(db, record):
    """Insert/Override data in the DB, prompting user for confirmation

    :param db (TinyDB DB or Table): database or table to look up in
    :param record (dict): key-value pairs to add to DB
    """
    if "DO_NOT_USE" in record:
        raise ValueError("records may not contain the key 'DO_NOT_USE'; I don't know what you expected")

    subrecord = {}
    for k in organizational_keys:
        x = record.get(k)
        if x is not None:
            subrecord[k] = x

    blanks_q = blanks_query(subrecord.keys())

    conflicts = {}
    existing_records = db.search(blanks_query & q.fragment(subrecord))
    for k in record.keys():
        if k in organizational_keys:
            continue
        for r in existing_records:
            if r.get(k) is not None:
                if conflicts.get(k) is None:
                    conflicts[k] = []
                conflicts[k].append(r[k])
        if conflicts.get(k) is not None:
            conflicts[k].append(record[k])
    if len(conflicts) > 0:
        print("new records conflict with existing data:\n %s\n" % conflicts)
        cont_input = input("continue, overriding old data? (y/N) ")
        if not coerce_bool_input(cont_input):
            return
    return db.upsert(record, blanks_query & q.fragment(subrecord))


def coerce_bool_input(inpt, default=False):
    coerced = inpt.strip().lower()
    if coerced == "y" or coerced == "yes":
        b = True
    elif coerced == "n" or coerced == "no" or coerced == "":
        b = False
    else:
        print("Didn't understand response, defaulting to no")
        b = False
    return b
