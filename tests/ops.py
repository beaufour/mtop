import types
import unittest

from attrdict import AttrDict

from mtop.lib.util import get_connection
from mtop.lib.util import op_cmp
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

    def test_op_sort(self):
        lst = [AttrDict({'active': True, 'opid': 2}),
               AttrDict({'active': True, 'opid': 1})]
        lst.sort(op_cmp)
        self.assertEqual([op.opid for op in lst], [1,2])

        lst = [AttrDict({'active': True, 'opid': 2}),
               AttrDict({'active': False, 'opid': 1})]
        lst.sort(op_cmp)
        self.assertEqual([op.opid for op in lst], [2,1])

if __name__ == '__main__':
    unittest.main()
