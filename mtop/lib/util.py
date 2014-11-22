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


def op_cmp(op1, op2):
    """
    Compare an operation by active and then opid.
    """
    if op1['active'] != op2['active']:
        return -1 if op1['active'] else 1

    return cmp(op1['opid'], op2['opid'])


def stringify_query_dict(query):
    for k, v in query.iteritems():
        if isinstance(v, dict):
            query[k] = stringify_query_dict(v)
        elif isinstance(v, Binary):
            query[k] = "bin:" + hex(v)
        elif isinstance(v, basestring):
            pass
        else:
            query[k] = str(v)
    return query
