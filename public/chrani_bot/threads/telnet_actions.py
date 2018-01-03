import re
from threading import Thread, Event
from ..rabaDB.rabaSetup import *
import atexit
from ..tools import timeout_occurred


class TelnetActions(Thread):
    """
    for now this loop observes all telnet activity and acts on it.
    it is getingt all match-strings and their handlers passed in by the constructor so we can
    chose which functions we want. there will be no sanity checks, the admin needs to know which commands
    require others for now
    """
    Player = None  # will hold the players rabaDB object
    Location = None  # will hold the locations rabaDB object
    tn_cmd = None  # telnetCommand class
    tn = None  # telnet socket for convenience (could simply use tn_cmd.tn)
    timeout_in_seconds = 0  # stop script after (timeout) seconds, regardless of activity
    print_status_frequency_loop_count = 0  # iterations of the loop
    print_status_frequency = 10  # print status every <print_status_frequency> loop
    actions = None  # methods stored in here will be executed by the loop!
    match_types = None
    loop_waiting_time = 1

    def __init__(self, event, tn, player, location, timeout = 0):
        self.tn_cmd = tn
        self.tn = self.tn_cmd.tn
        self.Player = player
        self.Location = location
        self.timeout_in_seconds = timeout
        Thread.__init__(self)
        self.stopped = event
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.tn:
            self.tn.close()
        print "telnet-observer has been shut down"

    def run(self):
        """
        I'm throwing everything in here I can think of
        the plan is to have this loop execute periodically to scan for new
        telnet-lines issued by the game. for now I will hardcode most things,
        eventually all functions should be modules that can dynamically link
        into the loop somehow
        """
        print "bot is ready and listening"
        self.tn_cmd.togglechatcommandhide(self.tn, "/")
        self.tn_cmd.send_message(self.tn, "[FFD700]Hi there. Command me![-]")
        script_start = time.time()
        next_observation = 0
        while not self.stopped.wait(next_observation) and not timeout_occurred(self.timeout_in_seconds, script_start):
            # calling this every second for testing
            try:
                response = self.tn.read_until(b"\r\n", 2)
            except Exception:
                response = "\r\n"
                self.loop_waiting_time = 10

            profiling_start = time.time()

            # match types need to be set in the main file of this script and then injected
            # unless you don't want the bot to do anything at all :)
            for match_type in self.match_types:
                m = re.search(self.match_types[match_type], response)
                # match chat messages
                if m:
                    player_name = m.group('player_name')
                    player = self.Player(name=player_name)  # used in the eval further down!!
                    connection = self.tn_cmd  # used in the eval further down!!
                    command = m.group('command')

                    if self.actions is not None:
                        for action in self.actions:
                            if action[0] == "isequal":
                                temp_command = command
                            if action[0] == "startswith":
                                temp_command = command.split(' ', 1)[0]

                            if action[1] == temp_command:
                                print "action"
                                #  function_matchtype = action[0]
                                function_name = action[2]
                                function_parameters = eval(action[3])  # yes. Eval. It's my own data, chill out!
                                function_name(*function_parameters)

            profiling_end = time.time()
            profiling_time = profiling_end - profiling_start
            next_observation = self.loop_waiting_time - profiling_time

            if self.print_status_frequency_loop_count == self.print_status_frequency or self.print_status_frequency_loop_count == 0:
                self.print_status_frequency_loop_count = 0
                print "telnet-observer is alive ({0} bytes received, execution-time: {1} seconds)".format(str(len(response)), str(round(profiling_time, 3)).ljust(5, '0'))
            self.print_status_frequency_loop_count += 1

        self.stopped.set()
