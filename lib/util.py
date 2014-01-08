from bson.binary import Binary


def op_cmp(op1, op2):
    """
    Compare an operation by active and then opid.
    """
    if op1['active'] != op2['active']:
        return -1 if op1['active'] else 1

    return cmp(op1['opid'], op2['opid'])


def stringify_query(query):
    for k, v in query.iteritems():
        if isinstance(v, dict):
            stringify_query(v)
        elif isinstance(v, Binary):
            query[k] = "bin:" + hex(v)
        else:
            query[k] = str(v)
    return query
