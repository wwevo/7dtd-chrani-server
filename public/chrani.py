#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
import telnetlib
import re
import time
import ConfigParser  # only needed for fancy config import
from threading import Thread, Event
from rabaDB.rabaSetup import *
import rabaDB.Raba as R
import rabaDB.fields as rf
import atexit

# import config options
# I like to kee them out of the way for the versioning system, a config file
# seems to be a sensible way
config = ConfigParser.ConfigParser()
config.read("../private/passwords.txt")
bot_suffix = "hoop"
HOST = config.get("telnet_" + bot_suffix, "telnet_host")
PORT = config.get("telnet_" + bot_suffix, "telnet_port")
PASS = config.get("telnet_" + bot_suffix, "telnet_pass")

RabaConfiguration('chrani_server', '../private/db/' + bot_suffix + '.db')


class Player(R.Raba):
    _raba_namespace = 'chrani_server'

    id = rf.Primitive()
    name = rf.Primitive()
    # I'd like to have coordinates as their own class, it's lame to do them one by one (x,y,z)
    pos_x = rf.Primitive()
    pos_y = rf.Primitive()
    pos_z = rf.Primitive()
    rot_x = rf.Primitive()
    rot_y = rf.Primitive()
    rot_z = rf.Primitive()
    remote = rf.Primitive()
    health = rf.Primitive()
    deaths = rf.Primitive()
    zombies = rf.Primitive()
    players = rf.Primitive()
    score = rf.Primitive()
    level = rf.Primitive()
    steamid = rf.Primitive()
    ip = rf.Primitive()
    ping = rf.Primitive()
    authenticated = rf.Primitive()

    def __init__(self):
        pass


class Location(R.Raba):
    _raba_namespace = 'chrani_server'

    owner = rf.RabaObject('Player')
    name = rf.Primitive()
    pos_x = rf.Primitive()
    pos_y = rf.Primitive()
    pos_z = rf.Primitive()

    def __init__(self):
        pass


class TelnetCommand:
    command_tn = None

    def __init__(self):
        while self.command_tn is None:
            self.command_tn = TelnetCommand.get_connection()
        print "TelnetCommands telnet connection has been opened"
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.command_tn: self.command_tn.close()
        print "TelnetCommands telnet connection has been closed"

    @staticmethod
    def get_connection():
        """
        for now, until i know better, i want each part of this bot using
        their own telnet. i'm not actually sure if it works that way, but it seems
        like it ^^
        """
        try:
            connection = telnetlib.Telnet(HOST, PORT)
            TelnetCommand.authenticate(connection)
            return connection
        except Exception, err:
            print "could not connect to the games telnet"
            time.sleep(4)

        return None

    @staticmethod
    def authenticate(connection):
        # this is the exact prompt from the games telnet. it might change with a new game-version
        password_prompt = connection.read_until("Please enter password:")
        connection.write(PASS.encode('ascii') + b"\r\n")
        # last 'welcome' line from the games telnet. it might change with a new game-version
        return connection.read_until("Press 'exit' to end session.")

    def send_message(self, message):
        response = None
        send_message_response_raw = ""

        self.command_tn.write("say \"" + message + b"\"\r\n")
        while send_message_response_raw == "" or response:
            response = self.command_tn.read_until(b"\r\n")
            send_message_response_raw = send_message_response_raw + response

            if re.match(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + re.escape(message) + "\r", response) is not None:
                return send_message_response_raw

    def send_private_message(self, player, message):
        response = None
        send_message_response_raw = ""

        self.command_tn.write("say \"" + message + b"\"\r\n")

        while send_message_response_raw == "" or response:
            response = self.command_tn.read_until(b"\r\n")
            send_message_response_raw = send_message_response_raw + response

            if re.match(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + re.escape(message) + "\r", response) is not None:
                return send_message_response_raw


class PollPlayers(Thread):
    poll_frequency = 2
    poll_players_tn = None
    poll_players_response_time = 0  # record the runtime of the entire poll

    class PlayerList(Thread):
        """
        I've put this in here cause it's never gonna be needed
        outside of PollPlayers.
        """
        poll_players_raw = None
        poll_players_array = None

        def __init__(self, event, list_players_raw):
            Thread.__init__(self)
            self.stopped = event
            self.poll_players_raw = list_players_raw

        def run(self):
            self.update(self.poll_players_raw)
            self.stopped.set()

        def update(self, poll_players_raw):
            player_line_regexp = r"\d{1,2}. id=(\d+), ([\w+]+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\n*"
            for m in re.finditer(player_line_regexp, poll_players_raw):
                """
                m.group(16) = steamid
                """
                try:
                    player = Player(steamid = m.group(16))
                except KeyError:
                    player = Player()

                player.id = m.group(1)
                player.name = m.group(2)
                player.pos_x = m.group(3)
                player.pos_y = m.group(4)
                player.pos_z = m.group(5)
                player.rot_x = m.group(6)
                player.rot_y = m.group(7)
                player.rot_z = m.group(8)
                player.remote = m.group(9)
                player.health = m.group(10)
                player.deaths = m.group(11)
                player.zombies = m.group(12)
                player.players = m.group(13)
                player.score = m.group(14)
                player.level = m.group(15)
                player.steamid = m.group(16)
                player.ip = m.group(17)
                player.ping = m.group(18)
                player.save()

    def __init__(self, event):
        while self.poll_players_tn is None:
            self.poll_players_tn = TelnetCommand.get_connection()
        print "PollPlayers telnet connection has been opened"

        Thread.__init__(self)
        self.stopped = event
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.poll_players_tn: self.poll_players_tn.close()
        print "PollPlayers loop has been shut down"

    def run(self):
        """
        recorded the runtime of the poll, using it to calculate the exact wait
        time between executions
        """
        print "playe poll is ready and listening"
        next_poll = 0;
        while not self.stopped.wait(next_poll):
            """
            basically an endless loop
            fresh player-data is about the most important thing for this bot :)
            """
            next_poll = self.poll_frequency - self.poll_players_response_time
            list_players_raw, player_count = self.poll_players()
            print "player-data poll is active ({0} players, {1} bytes received, response-time: {2} seconds)".format(str(player_count), str(len(list_players_raw)), str(round(self.poll_players_response_time, 3)).ljust(5, '0'))

            # not sure if this is the way to go, but I wanted to have this in it's own thread so the time spend in the
            # actual server-transaction won't be delayed
            store_player_list_event = Event()
            store_player_list_thread = self.PlayerList(store_player_list_event, list_players_raw)
            store_player_list_thread.start()

    def poll_players(self):
        """
        polls live player data from the games telnet
        times the action to allow for more accurate wait time
        returns complete telnet output and player count
        """
        profile_timestamp_start = time.time()

        list_players_response_raw = ""
        self.poll_players_tn.write("lp" + b"\r\n")
        while list_players_response_raw == "" or response:
            """
            fetches the response of the games telnet 'lp' command
            (lp = list players)
            last line from the games lp command, the one we are matching,
            might change with a new game-version
            """
            response = self.poll_players_tn.read_until(b"\r\n")
            list_players_response_raw = list_players_response_raw + response

            m = re.search(r"^Total of (\d{1,2}) in the game\r\n", response)
            if m:
                player_count = m.group(1)
                self.poll_players_response_time = time.time() - profile_timestamp_start
                return list_players_response_raw, player_count


class TelnetObserverLoop(Thread):
    """
    Only mandatory function for the bot!
    """
    loop_tn = None
    timeout_in_seconds = 4

    def __init__(self, event):
        while self.loop_tn is None:
            self.loop_tn = TelnetCommand.get_connection()
        print "ChatObservers telnet connection has been opened"

        Thread.__init__(self)
        self.stopped = event
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.loop_tn: self.loop_tn.close()
        print "ChatObserver loop has been shut down"

    def run(self):
        """
        I'm throwing everything in here I can think of
        the plan is to have this loop execute periodically to scan for new
        telnet-lines issued by the game. for now I will hardcode most things,
        eventually all functions should be modules that can dynamically link
        into the loop somehow
        """
        tn_cmd = TelnetCommand()
        print "bot is ready and listening"
        tn_cmd.send_message("Hi there. Command me!")
        timeout_start = None
        execution_time = 0.0
        while not self.stopped.wait(1):
            # calling this every second for testing, can be reduced for production and
            # further reduced after optimizations
            response = self.loop_tn.read_until(b"\r\n", 2)
            # print response
            print "chat-observer is alive ({0} bytes received, execution-time: {1} seconds)".format(str(len(response)), str(round(execution_time, 3)).ljust(5, '0'))
            """
            get a flowing timestamp going
            implement simple timeout function for debug and testing
            """
            latest_timestamp = time.time()
            if self.timeout_in_seconds != 0:
                if timeout_start is None:
                    timeout_start = time.time()
                elapsed_time = latest_timestamp - timeout_start
                if elapsed_time >= self.timeout_in_seconds:
                    """
                    no idea if this is really neccessary...
                    don't know where to close the thread otherwise
                    if statement, cause the eventit might not be present
                    """
                    print "scheduled timeout occured after {0} seconds".format(str(int(elapsed_time)))
                    break

            # group(1) = datetime, group(2) = stardate?, group(3) = bot command
            m = re.search(r"^(.+?) (.+?) INF Chat: \'(.*)\': \/(.+)\r", response)
            # match specific chat messages
            if m:
                player_name = m.group(3)
                player = Player(name = player_name)
                command = m.group(4)
                steamid = player.steamid

                if command == "set up lobby":
                    if player.authenticated:
                        try:
                            location = Location(name = 'lobby')
                        except KeyError:
                            location = Location()
                            location.name = 'lobby'

                        location.pos_x = player.pos_x
                        location.pos_y = player.pos_y
                        location.pos_z = player.pos_z
                        location.save()

                        tn_cmd.send_message(player_name + " has set up a lobby. Good job!")
                    else:
                        tn_cmd.send_message(player_name + " needs to enter the password to get access to sweet commands!")

                elif command == "make this my home":
                    if player.authenticated:
                        try:
                            location = Location(owner = player, name = 'home')
                        except KeyError:
                            location = Location()
                            location.name = 'home'
                            location.owner = player

                        location.pos_x = player.pos_x
                        location.pos_y = player.pos_y
                        location.pos_z = player.pos_z
                        location.save()

                        tn_cmd.send_message(player_name + " has decided to settle down!")
                    else:
                        tn_cmd.send_message(player_name + " needs to enter the password to get access to sweet commands!")

                elif command == "take me home":
                    if player.authenticated:
                        try:
                            location = Location(owner=player, name='home')
                            pos_x = location.pos_x
                            pos_y = location.pos_y
                            pos_z = location.pos_z
                            teleport_command = "teleportplayer " + steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                            print teleport_command
                            self.loop_tn.write(teleport_command)
                            tn_cmd.send_message(player_name + " got homesick")
                        except KeyError:
                            tn_cmd.send_message(player_name + " is apparently homeless...")
                    else:
                        tn_cmd.send_message(player_name + " needs to enter the password to get access to sweet commands!")

                elif command == "man, where's my pack?":
                    if player.authenticated:
                        try:
                            location = Location(owner=player, name='final_resting_place')
                            pos_x = location.pos_x
                            pos_y = location.pos_y
                            pos_z = location.pos_z
                            teleport_command = "teleportplayer " + steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                            print teleport_command
                            self.loop_tn.write(teleport_command)
                            tn_cmd.send_message(player_name + " is laaaaazy :)")
                        except KeyError:
                            tn_cmd.send_message(player_name + " believes to be dead oO")
                    else:
                        tn_cmd.send_message(player_name + " needs to enter the password to get access to sweet commands!")

                elif command.startswith("password "):
                    p = re.search(r"password (.+)", command)
                    if p:
                        password = p.group(1)
                        if password == "openup":
                            print "correct password!!"
                            if player.authenticated:
                                tn_cmd.send_message(player_name + ", we trust you already <3")
                            else:
                                try:
                                    location = Location(owner=player, name='spawn')
                                    player.authenticated = True
                                    pos_x = location.pos_x
                                    pos_y = location.pos_y
                                    pos_z = location.pos_z
                                    teleport_command = "teleportplayer " + steamid + " " + str(
                                        int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(
                                        int(float(pos_z))) + "\r\n"
                                    print teleport_command
                                    self.loop_tn.write(teleport_command)
                                    tn_cmd.send_message(player_name + " joined the ranks of literate people. Welcome!")
                                except KeyError:
                                    tn_cmd.send_message(player_name + " has no place of origin it seems")
                        else:
                            tn_cmd.send_message(player_name + " has entered a wrong password oO!")
                else:
                    tn_cmd.send_message("the command '" + command + "' is unknown to me :)")

            m = re.search(r"^(.+?) (.+?) INF GMSG: Player '(.*)' joined the game\r", response)
            if m:
                player_name = m.group(3)
                player = Player(name = player_name)
                steamid = player.steamid

                try:
                    location = Location(owner=player, name='spawn')
                    tn_cmd.send_message("Welcome back " + player_name + " o/")
                except KeyError:
                    location = Location()
                    location.name = 'spawn'
                    location.owner = player
                    location.pos_x = player.pos_x
                    location.pos_y = player.pos_y
                    location.pos_z = player.pos_z
                    location.save()
                    tn_cmd.send_message("this servers bot says Hi to " + player_name + " o/")

                if not player.authenticated:
                    try:
                        location = Location(name = 'lobby')
                        pos_x = location.pos_x
                        pos_y = location.pos_y
                        pos_z = location.pos_z
                        tn_cmd.send_message("your ass will be ported to our lobby until you have entered the password")
                        tn_cmd.send_message("read the rules on https://chrani.net/rules")
                        tn_cmd.send_message("enter the password with /password <password> in this chat")
                        teleport_command = "teleportplayer " + steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                        print teleport_command
                        self.loop_tn.write(teleport_command)
                    except KeyError:
                        pass

            m = re.search(r"^(.+?) (.+?) INF GMSG: Player '(.*)' died\r", response)
            if m:
                player_name = m.group(3)
                player = Player(name=player_name)
                steamid = player.steamid

                try:
                    location = Location(owner=player, name='final_resting_place')
                except KeyError:
                    location = Location()
                    location.name = 'final_resting_place'
                    location.owner = player

                location.pos_x = player.pos_x
                location.pos_y = player.pos_y
                location.pos_z = player.pos_z
                location.save()

            m = re.search(r"^(.+?) (.+?) INF .* \(reason: Died, .* PlayerName='(.*)'\r", response)
            if m:
                player_name = m.group(3)
                player = Player(name=player_name)
                steamid = player.steamid
                if not player.authenticated:
                    try:
                        location = Location(name = 'lobby')
                        pos_x = location.pos_x
                        pos_y = location.pos_y
                        pos_z = location.pos_z
                        teleport_command = "teleportplayer " + steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                        print teleport_command
                        self.loop_tn.write(teleport_command)
                        tn_cmd.send_message("there is no escape from the lobby!")
                    except KeyError:
                        pass
                else:
                    tn_cmd.send_message("type /man, where's my pack? in this chat to return to your backpack!")
            chat_line_scan_time = time.time()
            execution_time = chat_line_scan_time - latest_timestamp
        self.stopped.set()


if __name__ == '__main__':
    """
    mandatory threads! all other thread will be shut down if this one is missing  
    """
    telnet_observer_event = Event()
    telnet_observer_thread = TelnetObserverLoop(telnet_observer_event)
    telnet_observer_thread.start()

    """
    optional threads. depend on global loop to be running
    it is the plan that they can inject chat listeners into the main loop
    this needs some planning, will be required before we start with big additions though 
    """
    player_poll_loop_event = Event()
    player_poll_loop_thread = PollPlayers(player_poll_loop_event)
    player_poll_loop_thread.setDaemon(True) # thread get's shut down when all non daemon threads have ended
    player_poll_loop_thread.start()

