import re
from threading import Thread, Event
from rabaDB.rabaSetup import *
import atexit


class TelnetObserver(Thread):
    """
    for now this loop observes all telnet activity and acts on it.
    in the future, it will get all match-strings and their handlers passed in by the constructor so we can
    chose which functions we want. there will be no sanity checks, the admin has to know which commands
    require others
    """
    Player = None  # will hold the players rabaDB object
    Location = None  # will hold the locations rabaDB object
    tn_cmd = None  # telnetCommand class
    tn = None  # telnet socket for convenience (could simply use tn_cmd.tn)
    timeout_in_seconds = 0  # stop script after (timeout) seconds, regardless of activity
    actions = None

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

    @staticmethod
    def timeout_occurred(timeout_in_seconds, timeout_start):
        if timeout_in_seconds != 0:
            if timeout_start is None:
                timeout_start = time.time()
            elapsed_time = time.time() - timeout_start
            if elapsed_time >= timeout_in_seconds:
                print "scheduled timeout occurred after {0} seconds".format(str(int(elapsed_time)))
                return True
        return None

    def password(self, player, command, connection):
        p = re.search(r"password (.+)", command)
        if p:
            password = p.group(1)
            if password == "openup":
                print "correct password!!"
                if player.authenticated:
                    connection.send_message(connection.tn, player.name + ", we trust you already <3")
                else:
                    try:
                        location = self.Location(owner=player, name='spawn')
                        pos_x = location.pos_x
                        pos_y = location.pos_y
                        pos_z = location.pos_z
                        teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(
                            int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                        print teleport_command
                        connection.tn.write(teleport_command)
                        connection.send_message(connection.tn, player.name + " joined the ranks of literate people. Welcome!")
                    except KeyError:
                        connection.send_message(connection.tn, player.name + " has no place of origin it seems")
                    finally:
                        player.authenticated = True

            else:
                connection.send_message(connection.tn, player.name + " has entered a wrong password oO!")

    def run(self):
        """
        I'm throwing everything in here I can think of
        the plan is to have this loop execute periodically to scan for new
        telnet-lines issued by the game. for now I will hardcode most things,
        eventually all functions should be modules that can dynamically link
        into the loop somehow
        """
        print "bot is ready and listening"
        # self.tn_cmd.send_message(self.tn, "Hi there. Command me!")
        script_start = time.time()
        while not self.stopped.wait(1) and not self.timeout_occurred(self.timeout_in_seconds, script_start):
            # calling this every second for testing
            response = self.tn.read_until(b"\r\n", 2)
            profiling_start = time.time()

            # group(1) = datetime, group(2) = stardate?, group(3) = player_name group(4) = bot command
            m = re.search(r"^(.+?) (.+?) INF Chat: \'(.*)\': /(.+)\r", response)
            # match chat messages
            if m:
                player_name = m.group(3)
                player = self.Player(name=player_name)
                command = m.group(4)

                if command is not None:
                    actions = self.actions.get(command)
                    if actions is not None:
                        for action in actions:
                            print "action"
                            action[0](self, player, self.tn_cmd)

                if command.startswith("password "):
                    self.password(player, command, self.tn_cmd)

            m = re.search(r"^(.+?) (.+?) INF GMSG: Player '(.*)' (.*)\r", response)
            # player_events
            if m:
                player_name = m.group(3)
                player = self.Player(name=player_name)
                command = m.group(4)

                if command is not None:
                    actions = self.actions.get(command)
                    if actions is not None:
                        for action in actions:
                            print "action"
                            action[0](self, player, self.tn_cmd)

            m = re.search(r"^(.+?) (.+?) INF PlayerSpawnedInWorld \(reason: (.+?), .* PlayerName='(.*)'\r", response)
            if m:
                command = m.group(3)
                player_name = m.group(4)
                player = self.Player(name=player_name)

                if command is not None:
                    actions = self.actions.get(command)
                    if actions is not None:
                        for action in actions:
                            print "action"
                            action[0](self, player, self.tn_cmd)

            profiling_end = time.time()
            profiling_time = profiling_end - profiling_start
            print "telnet-observer is alive ({0} bytes received, execution-time: {1} seconds)".format(str(len(response)), str(round(profiling_time, 3)).ljust(5, '0'))
        self.stopped.set()
