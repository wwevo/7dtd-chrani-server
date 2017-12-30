import time


def timeout_occurred(timeout_in_seconds, timeout_start):
    if timeout_in_seconds != 0:
        if timeout_start is None:
            timeout_start = time.time()
        elapsed_time = time.time() - timeout_start
        if elapsed_time >= timeout_in_seconds:
            print "scheduled timeout occurred after {0} seconds".format(str(int(elapsed_time)))
            return True
    return None


class ObjectView(object):
    def __init__(self, d):
        self.__dict__ = d

