"""
This script starts a number of virtual machines
"""

import startami
import threading
import sys

class recordingState(object):
    def __init__(self, howMany):
        self._lock = threading._allocate_lock()
        self._results = {}
        self._finished = 0
        self._total = howMany

    def recordSuccess(self, id, msg=''):
        self._lock.acquire()
        self._results[id] = {'result': 'success', 'msg': msg}
        self._updateCount()
        self._lock.release()

    def recordFailure(self, id, msg=''):
        self._lock.acquire()
        self._results[id] = {'result': 'failure', 'msg': msg}
        self._updateCount()
        self._lock.release()

    def _updateCount(self):
        self._finished += 1
        print "%d finished, %d remaining" % (self._finished, self._total - self._finished)

    def __str__(self):
        self._lock.acquire()
        keys = self._results.keys()
        keys.sort()
        successes = 0
        for key in keys:
            if self._results[key]['result'] == 'success':
                successes += 1

        print "%d succeeded, %d failed" % (successes, len(keys) - successes)
        for id in keys:
            print "id: %d, result: '%s', msg: '%s'" % (id, self._results[id]['result'],
                                                       self._results[id]['msg'])
        self._lock.release()

def startinstance(rcs, id=1):
    """
    This method starts an instance with some default
    paramaters, catching any errors and writing their
    output to stdout
    """
    try:
        result = startami.startami('ubuntu1004x64', 'm1.large', 'AKIAIPTGCRTMWK3JGNDQ', 'rBw1BDAdEjX72ZF9us4WtH+Jvb2cOei6rMkQshKo',
                                   'my_key_pair')
    except Exception as exc:
        rcs.recordFailure(id, 'exception: %s' % str(exc))
        return

    rcs.recordSuccess(id)

if __name__ == '__main__':
    defaultNumber = 10
    if len(sys.argv) == 2:
        defaultNumber = int(sys.argv[1])

    if defaultNumber > 20:
        print "cannot start more than 20 instances at once, capping at 20"
        defaultNumber = 20

    rcs = recordingState(howMany=defaultNumber)
    print "starting %d instances" % defaultNumber
    threads = []
    for i in xrange(0, defaultNumber):
        t = threading.Thread(target=startinstance, kwargs={'id':i, 'rcs': rcs})
        t.start()
        threads.append(t)

    print "%d threads started, joining()..." % defaultNumber
    for t in threads:
        t.join()

    print "results:"
    print rcs
