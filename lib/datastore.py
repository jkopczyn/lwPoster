import os
from tinydb import TinyDB, Query
from itertools import combinations

DIRECTORY = os.path.dirname(os.path.abspath(__file__))

database = TinyDB(DIRECTORY + '/parameter-store.json')
input_values_table = database.table('input_values')
locations_table = database.table('locations')
output_forms_table = database.table('output_formats')

secrets_database = TinyDB(DIRECTORY + '/secrets-store.json')

organizational_keys_map = {
    input_values_table: ["rich_text", "meetup_series", "topic"],
    locations_table: ["location"],
    output_forms_table: ["rich_text", "destination"],
    secrets_database: ["meetup_series"],
}
q = Query()


def lookup_with_overrides(db, primary_keys):
    """Check for all stored values for a particular set of params. Start with the default values and
    override them with queries of increasing specificity based on the provided params.

    :param db (TinyDB DB or Table): database or table to look up in
    :param primary_keys (dict[string][string/other]): organizational keys to query by
    """
    if db not in organizational_keys_map:
        raise ValueError("cannot look up in table without known organizational keys")
    organizational_keys = organizational_keys_map[db]

    extra_keys = set(primary_keys.keys()) - set(organizational_keys)
    if extra_keys:
        raise ValueError(str(extra_keys)+" are not valid organizational keys")

    keys_to_queries = {key: ~(q[key].exists()) for key in organizational_keys}
    live_keys = {key: False for key in organizational_keys}

    for key in primary_keys.keys():
        v = primary_keys[key]
        if str(v) == v:
            key_q = q[key] == v
        else:
            key_q = q[key].map(lambda x: str(x).lower()) == str(v).lower()
        keys_to_queries[key] = key_q
        live_keys[key] = True

    blank_q = blanks_query(db, [])
    defaults = merged_query(db, blank_q)

    for key in organizational_keys:
        if not live_keys[key]:
            continue
        key_query = query_plus_organizational_blanks(db, keys_to_queries[key], [key])
        merged_result = merged_query(db, key_query)
        defaults.update(merged_result)

    for length in range(2,len(organizational_keys)):
        for keys in combinations(organizational_keys, length):
            if not all(live_keys[k] for k in keys):
                continue
            query_list = list(keys_to_queries[key] for key in keys)
            grouped_queries = intersect_queries(query_list)
            key_query = query_plus_organizational_blanks(db, grouped_queries, list(keys))
            merged_result = merged_query(db, key_query)
            defaults.update(merged_result)

    if all(live_keys[k] for k in organizational_keys):
        grouped_queries = intersect_queries(keys_to_queries[key] for key in organizational_keys)
        merged_result = merged_query(grouped_queries)
        defaults.update(merged_result)

    return defaults


def intersect_queries(queries):
    """Take a list of queries and combine them with &.

    Must be a list, not an iterator. The obvious patches just caused more problems.
    """
    if len(queries) == 0:
        return Query()
    q = queries[0]
    idx = 1
    while idx < len(queries):
        q = q & queries[idx]
        idx += 1
    return q


def query_plus_organizational_blanks(table, query, nonblank_keys):
    return blanks_query(table, nonblank_keys, query)


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


def blanks_query(table, nonblank_keys, initial_query=None):
    queries = []
    if initial_query is not None:
        queries = [initial_query]

    for k in organizational_keys_map[table]:
        if k in nonblank_keys:
            continue
        queries.append(~(q[k].exists()))
    return intersect_queries(queries)


def interactive_insert_data(db, record):
    """Insert/Override data in the DB, prompting user for confirmation

    :param db (TinyDB DB or Table): database or table to look up in
    :param record (dict): key-value pairs to add to DB
    """
    subrecord = {}
    for k in organizational_keys_map[db]:
        x = record.get(k)
        if x is not None:
            subrecord[k] = x

    blanks_q = blanks_query(db, subrecord.keys())

    conflict_context = []
    conflicts = {}
    existing_records = db.search(blanks_q & q.fragment(subrecord))
    for k in record.keys():
        if k in organizational_keys_map[db]:
            conflict_context.append(k)
            continue
        for r in existing_records:
            if r.get(k) is not None:
                if conflicts.get(k) is None:
                    conflicts[k] = []
                conflicts[k].append(r[k])
        if conflicts.get(k) is not None:
            conflicts[k].append(record[k])
    if len(conflicts) > 0:
        print(
                "new records [for %s] conflict with existing data:\n %s\n" % (
                    conflict_context, conflicts)
                )
        cont_input = input("continue, overriding old data? (y/N) ")
        if not coerce_bool_input(cont_input):
            return
    return db.upsert(record, blanks_q & q.fragment(subrecord))


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


def insert_file_contents(db, record, key, filename):
    file = open(filename, 'r')
    contents = file.read().rstrip()
    record.update({key: contents})
    return interactive_insert_data(db, record)


def store_secrets(
        meetup_series,
        gmail_username,
        gmail_app_password,
        fb_login_email,
        phone_number,
        maps_key,
        lw_username,
        lw_temporary_key,
        ):
    record = {
            "meetup_series": meetup_series || None,
            "gmail_username": gmail_username || None,
            "gmail_app_password": gmail_app_password || None,
            "fb_login_email": fb_login_email || None,
            "phone_number": phone_number || None,
            "maps_key":  maps_key || None,
            "lw_username": lw_username || None,
            "lw_temporary_key": lw_temporary_key || None,
            }
    return interactive_insert_data(secrets_database, record)
