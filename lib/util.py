def op_cmp(op1, op2):
    """
    Compare an operation by active and then opid.
    """
    if op1['active'] != op2['active']:
        return -1 if op1['active'] else 1

    return cmp(op1['opid'], op2['opid'])
