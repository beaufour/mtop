from pymongo.errors import AutoReconnect

class MongoOps():
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
            ret = self._connection.db.command({'serverStatus': 1})
        except AutoReconnect:
            pass

        return ret
