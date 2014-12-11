import pymongo
from pymongo.errors import AutoReconnect

try:
    from bson.binary import Binary
except ImportError:
    # fall back to old location
    from pymongo.binary import Binary


def get_connection(server):
    try:
        # New pymongo
        if (hasattr(pymongo, 'version_tuple') and
                pymongo.version_tuple[0] >= 2 and
                pymongo.version_tuple[1] >= 4):
            from pymongo import MongoClient
            from pymongo.read_preferences import ReadPreference
            return MongoClient(host=server, read_preference=ReadPreference.SECONDARY)

        # Old pymongo
        from pymongo.connection import Connection
        return Connection(server, slave_okay=True)

    except AutoReconnect:
        return None


def op_key(op):
    """
    Returns a sort key that sorts by by active and then opid.
    """
    return '{0}{1}'.format('a' if op['active'] else 'i', op['opid'])


def is_string(value):
    """
    Test whether the value is a string, working on both Python 2 and 3.
    """
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)


def stringify_query_dict(query):
    for k, v in query.iteritems():
        if isinstance(v, dict):
            query[k] = stringify_query_dict(v)
        elif isinstance(v, Binary):
            query[k] = "bin:" + hex(v)
        elif is_string(v):
            pass
        else:
            query[k] = str(v)
    return query
