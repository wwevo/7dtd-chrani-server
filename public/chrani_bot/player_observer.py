import re
from threading import Thread, Event
from rabaDB.rabaSetup import *
import atexit
from tools import timeout_occurred


class PlayerObserver(Thread):
    """
    for now this loop observes all player activity and acts on it.
    in the future, it will get all match-strings and their handlers passed in by the constructor so we can
    chose which functions we want. there will be no sanity checks, the admin has to know which commands
    require others
    """
    timeout_in_seconds = 0  # stop script after (timeout) seconds, regardless of activity
    loop_waiting_time = 2  # time to wait between loops

    tn = None  # telnet socket for convenience (could simply use tn_cmd.tn)
    tn_cmd = None  # telnetCommand class

    Player = None  # will hold the players rabaDB object
    Location = None  # will hold the locations rabaDB object

    observers = None

    def __init__(self, event, tn, player, location, timeout=0):
        self.timeout_in_seconds = timeout

        self.tn_cmd = tn
        self.tn = self.tn_cmd.tn

        self.Player = player
        self.Location = location

        Thread.__init__(self)
        self.stopped = event
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.tn:
            self.tn.close()
        print "player-observer has been shut down"

    def run(self):
        """
        I'm throwing everything in here I can think of
        the plan is to have this loop execute periodically to monitor player
        and their movement, acting on set conditions
        for example
        ping-kicker
        kick player because of their name
        check proximity to locations (homes, lobby, prison etc)
        """
        print "playerobserver is ready! READAAAAY!!"
        self.tn_cmd.send_message(self.tn, "[FFD700]We are watching you![-]")
        script_start = time.time()
        while not self.stopped.wait(self.loop_waiting_time) and not timeout_occurred(self.timeout_in_seconds, script_start):
            profiling_start = time.time()

            if self.observers is not None:
                for observer in self.observers:
                    connection = self.tn_cmd  # used in the eval further down!!
                    function_name = observer[1]
                    function_parameters = eval(observer[2])  # yes. Eval. It's my own data, chill out!
                    function_name(*function_parameters)

            profiling_end = time.time()
            profiling_time = profiling_end - profiling_start
            print "player-observer is alive (execution-time: {0} seconds)".format(str(round(profiling_time, 3)).ljust(5, '0'))
        self.stopped.set()
