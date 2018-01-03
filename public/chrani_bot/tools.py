import time
import collections

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

def deep_update(source, overrides):
    """Update a nested dictionary or similar mapping.

    Modify ``source`` in place.
    """
    for key, value in overrides.iteritems():
        if isinstance(value, collections.Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source
