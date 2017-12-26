import atexit
import time
import re
from threading import Thread, Event
from rabaDB.rabaSetup import *
import atexit


class TelnetObserver(Thread):
    """
    Only mandatory function for the bot!
    """
    loop_tn = None
    tn_cmd = None
    tn = None
    timeout_in_seconds = 0

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
        if self.loop_tn: self.loop_tn.close()
        print "telnet-observer has been shut down"

    def timeout_occurred(self, timeout_in_seconds, timeout_start):
        if timeout_in_seconds != 0:
            if timeout_start is None:
                timeout_start = time.time()
            elapsed_time = time.time() - timeout_start
            if elapsed_time >= timeout_in_seconds:
                print "scheduled timeout occurred after {0} seconds".format(str(int(elapsed_time)))
                return True
        return None

    def set_up_lobby(self, player, connection):
        if player.authenticated:
            try:
                location = self.Location(name='lobby')
            except KeyError:
                location = self.Location()
                location.name = 'lobby'

            location.pos_x = player.pos_x
            location.pos_y = player.pos_y
            location.pos_z = player.pos_z
            location.save()

            connection.send_message(connection.tn, player.name + " has set up a lobby. Good job!")
        else:
            connection.send_message(connection.tn, player.name + " needs to enter the password to get access to sweet commands!")

    def make_this_my_home(self, player, connection):
        if player.authenticated:
            try:
                location = self.Location(owner=player, name='home')
            except KeyError:
                location = self.Location()
                location.name = 'home'
                location.owner = player

            location.pos_x = player.pos_x
            location.pos_y = player.pos_y
            location.pos_z = player.pos_z
            location.save()

            connection.send_message(connection.tn, player.name + " has decided to settle down!")
        else:
            connection.send_message(connection.tn, player.name + " needs to enter the password to get access to sweet commands!")

    def take_me_home(self, player, connection):
        if player.authenticated:
            try:
                location = self.Location(owner=player, name='home')
                pos_x = location.pos_x
                pos_y = location.pos_y
                pos_z = location.pos_z
                teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                # print teleport_command
                connection.tn.write(teleport_command)
                connection.send_message(connection.tn, player.name + " got homesick")
            except KeyError:
                connection.send_message(connection.tn, player.name + " is apparently homeless...")
        else:
            connection.send_message(connection.tn, player.name + " needs to enter the password to get access to sweet commands!")

    def man_where_is_my_pack(self, player, connection):
        if player.authenticated:
            try:
                location = self.Location(owner=player, name='final_resting_place')
                pos_x = location.pos_x
                pos_y = location.pos_y
                pos_z = location.pos_z
                teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                # print teleport_command
                connection.tn.write(teleport_command)
                connection.send_message(connection.tn, player.name + " is laaaaazy :)")
            except KeyError:
                connection.send_message(connection.tn, player.name + " believes to have died, but didn't oO")
        else:
            connection.send_message(connection.tn, player.name + " needs to enter the password to get access to sweet commands!")

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

    def on_player_join(self, player, connection):
        """
        ever newly logged in player will be handled here
        players will be greeted, a spawn will be set for new players
        if the player is not authenticated, he will be ported to the lobby, if one is set
        a prompt to enter the password will be displayed to unlock commands
        :param player: player-object pulled from database
        :param connection: Telnet command object
        :return: nothing to return
        """
        try:
            location = self.Location(owner=player, name='spawn')
            connection.send_message(connection.tn, "Welcome back " + player.name + " o/")
        except KeyError:
            location = self.Location()
            location.name = 'spawn'
            location.owner = player
            location.pos_x = player.pos_x
            location.pos_y = player.pos_y
            location.pos_z = player.pos_z
            location.save()
            connection.send_message(connection.tn, "this servers bot says Hi to " + player.name + " o/")

        if not player.authenticated:
            try:
                location = self.Location(name='lobby')
                pos_x = location.pos_x
                pos_y = location.pos_y
                pos_z = location.pos_z
                connection.send_message(connection.tn, "yo ass will be ported to our lobby plus tha command-shit is restricted yo")
                connection.send_message(connection.tn, "read the rules on https://chrani.net/rules")
                connection.send_message(connection.tn, "enter the password with /password <password> in this chat")
                teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                print teleport_command
                connection.tn.write(teleport_command)
            except KeyError:
                connection.send_message(connection.tn, "your account is restricted until you have read the rules")
                connection.send_message(connection.tn, "read the rules on https://chrani.net/rules")
                connection.send_message(connection.tn, "enter the password with /password <password> in this chat")

    def on_player_death(self, player):
        """
        saves location of the last death for a later return
        :param player: player-object
        :return: nothing to return
        """
        try:
            location = self.Location(owner=player, name='final_resting_place')
        except KeyError:
            location = self.Location()
            location.name = 'final_resting_place'
            location.owner = player

        location.pos_x = player.pos_x
        location.pos_y = player.pos_y
        location.pos_z = player.pos_z
        location.save()

    def on_respawn_after_death(self, player, connection):
        """
        scans for player respawn after death
        sends players who are not authenticated back to the lobby
        states to existing ones that they can port to it.
        does nothing if player is not authenticated and no lobby exists
        :param player: player-object pulled from database
        :param connection: Telnet command object
        :return: nothing to return
        """
        if not player.authenticated:
            try:
                location = self.Location(name='lobby')
                pos_x = location.pos_x
                pos_y = location.pos_y
                pos_z = location.pos_z
                teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                # print teleport_command
                self.tn.write(teleport_command)
                connection.send_message(connection.tn, "there is no escape from the lobby!")
            except KeyError:
                pass
        else:
            connection.send_message(connection.tn, "type /man, where's my pack? in this chat to return to your backpack!")

    def run(self):
        """
        I'm throwing everything in here I can think of
        the plan is to have this loop execute periodically to scan for new
        telnet-lines issued by the game. for now I will hardcode most things,
        eventually all functions should be modules that can dynamically link
        into the loop somehow
        """
        print "bot is ready and listening"
        self.tn_cmd.send_message(self.tn, "Hi there. Command me!")
        script_start = time.time()
        while not self.stopped.wait(1) and not self.timeout_occurred(self.timeout_in_seconds, script_start):
            # calling this every second for testing
            response = self.tn.read_until(b"\r\n", 2)
            profiling_start = time.time()

            # group(1) = datetime, group(2) = stardate?, group(3) = player_name group(4) = bot command
            m = re.search(r"^(.+?) (.+?) INF Chat: \'(.*)\': /(.+)\r", response)
            # match specific chat messages
            if m:
                player_name = m.group(3)
                player = self.Player(name=player_name)
                command = m.group(4)

                if command == "set up lobby":
                    self.set_up_lobby(player, self.tn_cmd)

                elif command == "make this my home":
                    self.make_this_my_home(player,  self.tn_cmd)

                elif command == "take me home":
                    self.take_me_home(player, self.tn_cmd)

                elif command == "man, where's my pack?":
                    self.man_where_is_my_pack(player, self.tn_cmd)

                elif command.startswith("password "):
                    self.password(player, command, self.tn_cmd)

                else:
                    self.tn_cmd.send_message(self.tn, "the command '" + command + "' is unknown to me :)")

            m = re.search(r"^(.+?) (.+?) INF GMSG: Player '(.*)' (.*)\r", response)
            # match specific Player-events
            if m:
                player_name = m.group(3)
                player = self.Player(name=player_name)
                command = m.group(4)

                if command == "joined the game":
                    self.on_player_join(player, self.tn_cmd)

                elif command == "died":
                    self.on_player_death(player, self.tn_cmd)

            m = re.search(r"^(.+?) (.+?) INF .* \(reason: Died, .* PlayerName='(.*)'\r", response)
            if m:
                player_name = m.group(3)
                player = self.Player(name=player_name)

                self.on_respawn_after_death(player)

            profiling_end = time.time()
            profiling_time = profiling_end - profiling_start
            print "telnet-observer is alive ({0} bytes received, execution-time: {1} seconds)".format(str(len(response)), str(round(profiling_time, 3)).ljust(5, '0'))
        self.stopped.set()
