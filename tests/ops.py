import types
import unittest

from mtop.lib.util import get_connection
from mtop.lib.ops import MongoOps

class TestOps(unittest.TestCase):
    def setUp(self):
        connection = get_connection('localhost')
        self._mongo_ops = MongoOps(connection)

    def test_server_status(self):
        ret = self._mongo_ops.get_server_status()
        self.assertTrue('version' in ret)

    def test_get_inprog(self):
        ret = self._mongo_ops.get_inprog()
        self.assertEqual(type(ret), types.ListType)

if __name__ == '__main__':
    unittest.main()
