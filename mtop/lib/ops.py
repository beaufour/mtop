from pymongo.errors import AutoReconnect
try:
    from bson.son import SON
except ImportError:
    # fall back to old location
    from pymongo.son import SON


class MongoOps(object):
    """
    Helper class for mongo commands we use.

    Wraps calls in try/except so that resizing does not break them.
    """

    def __init__(self, connection):
        """
        @param connection: pymongo Connection to use.
        """

        self._connection = connection

    def get_inprog(self):
        ret = None
        try:
            ret = self._connection.db['$cmd.sys.inprog'].find_one()
        except AutoReconnect:
            pass

        return ret['inprog'] if ret else []

    def get_server_status(self):
        ret = None
        try:
            ret = self._connection.db.command(SON([('serverStatus', 1),
                                                   ('repl', 2),
                                                   ['workingSet', 1],
                                                   ]))
        except AutoReconnect:
            pass

        return ret
