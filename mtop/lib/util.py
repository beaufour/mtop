try:
    from bson.binary import Binary
except ImportError:
    # fall back to old location
    from pymongo.binary import Binary


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
