import json
import time

from mtop.lib.ops import MongoOps
from mtop.lib.screen import Screen
from mtop.lib.util import op_key
from mtop.lib.util import stringify_query_dict


class Runner(object):
    """
    Main logic for 'mtop'. Once initialized, L{run()} keeps updating
    until ctrl-c is pressed.
    """

    def __init__(self, connection, interval):
        """
        @param connection: pymongo Connection to use.
        @param interval: Delay between updates (ms).
        """

        self._connection = connection
        self._timeout = interval / 1000.
        self._mongo_ops = MongoOps(self._connection)

    def run(self):
        """
        Run loop.

        @param screen: cursus screen object.
        @return: 0 if normal exit, negative values otherwise
        """

        self._screen = Screen()
        try:
            return self._do_run()
        except KeyboardInterrupt:
            pass
        finally:
            self._screen.end()

        return 0

    def _do_run(self):
        self._screen.timeout(self._timeout)
        self._last_opstats = {}
        self._maxy, self._maxx = self._screen.getmaxyx()

        if self._maxy < 5:
            return -3

        while True:
            self._y = 0

            srvstat = self._mongo_ops.get_server_status()
            inprog = self._mongo_ops.get_inprog()
            inprog.sort(key=op_key)

            self._screen.clear()
            if srvstat:
                self._server_stats(srvstat)
                self._memory_stats(srvstat)
                self._repl_stats(srvstat)
                self._op_stats(srvstat)

            if inprog:
                self._inprog(inprog)

            time.sleep(self._timeout)

            # In the event of a resize
            self._maxy, self._maxx = self._screen.getmaxyx()

    def _print(self, arr):
        try:
            self._screen.addstr(self._y, 0, ''.join(arr)[:self._maxx])
            self._y += 1
        except:
            pass

    def _server_stats(self, d):
        host = self._connection.host
        out = []
        out.append("%s. v%s, %d bit" % (host, d['version'], d['mem']['bits']))
        out.append('. Conns: %d/%d' % (d['connections']['current'], d['connections']['available']))
        ratio = d['globalLock'].get('ratio')
        if ratio is None:
            ratio = float(d['globalLock']['lockTime']) / float(d['globalLock']['totalTime'])
        out.append('. Lock %%: %.2f' % round(ratio, 2))
        self._print(out)

    def _memory_stats(self, d):
        out = []
        out.append('Mem (MB): %s resident, %s virtual, %s mapped' % (d['mem']['resident'],
                                                                     d['mem']['virtual'],
                                                                     d['mem']['mapped']))
        if 'workingSet' in d:
            # value is in pages (i.e. 4k blocks), so divide it by / 256 to get MB
            out.append(', %d working set' % (round(int(d['workingSet']['pagesInMemory']) / 256.0)))
        self._print(out)

    def _repl_stats(self, d):
        repl = d.get('repl')
        if not repl:
            return

        hosts = repl.get('hosts')
        if not hosts:
            return

        out = []
        out.append('Rep (%s):' % repl['setName'])
        for host in hosts:
            out.append(' %s(%s)' % (host, 'P' if host == repl['primary'] else 'S'))
        self._print(out)

    def _op_stats(self, d):
        out = []
        out.append('Ops:')
        ops = []
        total = 0
        for op in d['opcounters']:
            val = 0
            if op in self._last_opstats:
                val = d['opcounters'][op] - self._last_opstats[op]
            self._last_opstats[op] = d['opcounters'][op]
            ops.append(' %4d %s' % (val, op))
            total += val

        ops.insert(0, ' %4d total' % total)
        out.append(','.join(ops))
        self._print(out)

    def _inprog(self, inprog):
        template = "%11s %21s %7s %1s %5s %s"
        self._print([template % ('ID', 'CLIENT', 'OP', 'A', 'LOCKW', 'NS / QUERY')])

        opsmax = self._maxy - self._y
        if len(inprog) > opsmax:
            # Leave room for '% more' line
            opsmax -= 1

        for op in inprog[:opsmax]:
            a = 'T' if op['active'] else 'F'
            lock = op.get('lockType') if op['waitingForLock'] else ''
            client = op.get('client', 'internal')
            ns_query = op['ns']
            if client == 'internal':
                ns_query += op.get('desc', '')
            query = op.get('query')
            if query:
                ns_query += " " + json.dumps(stringify_query_dict(query))[:(self._maxx - 40)]
            self._print([template % (op['opid'], client, op['op'], a, lock, ns_query)])

        if len(inprog) > opsmax:
            self._print(['( ... %d more ... )' % (len(inprog) - opsmax)])
