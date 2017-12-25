#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
import re
import time
import ConfigParser  # only needed for fancy config import
from threading import Thread, Event
from rabaDB.rabaSetup import *
import rabaDB.Raba as R
import rabaDB.fields as rf
import atexit
from telnet_cmd import TelnetCommand
from poll_players import PollPlayers

# import config options
# I like to keep them out of the way for the versioning system, a config file
# seems to be a sensible way
bot_suffix = "hoop"

config = ConfigParser.ConfigParser()
config.read("../private/passwords.txt")
HOST = config.get("telnet_" + bot_suffix, "telnet_host")
PORT = config.get("telnet_" + bot_suffix, "telnet_port")
PASS = config.get("telnet_" + bot_suffix, "telnet_pass")

RabaConfiguration('chrani_server', '../private/db/' + bot_suffix + '.db')


class Player(R.Raba):
    _raba_namespace = 'chrani_server'

    id = rf.Primitive()
    name = rf.Primitive()
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


class TelnetObserverLoop(Thread):
    """
    Only mandatory function for the bot!
    """
    loop_tn = None
    timeout_in_seconds = 0

    def __init__(self, event, tn):
        self.loop_tn = tn
        Thread.__init__(self)
        self.stopped = event
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.loop_tn: self.loop_tn.close()
        print "telnet-observer has been shut down"

    def run(self):
        """
        I'm throwing everything in here I can think of
        the plan is to have this loop execute periodically to scan for new
        telnet-lines issued by the game. for now I will hardcode most things,
        eventually all functions should be modules that can dynamically link
        into the loop somehow
        """
        tn_cmd = TelnetCommand(HOST, PORT, PASS)
        print "bot is ready and listening"
        tn_cmd.send_message("Hi there. Command me!")
        timeout_start = None
        execution_time = 0.0
        while not self.stopped.wait(1):
            # calling this every second for testing, can be reduced for production and
            # further reduced after optimizations
            response = self.loop_tn.read_until(b"\r\n", 2)
            # print response
            print "telnet-observer is alive ({0} bytes received, execution-time: {1} seconds)".format(str(len(response)), str(round(execution_time, 3)).ljust(5, '0'))
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

            # group(1) = datetime, group(2) = stardate?, group(3) = player_name group(4) = bot command
            m = re.search(r"^(.+?) (.+?) INF Chat: \'(.*)\': \/(.+)\r", response)
            # match specific chat messages
            if m:
                player_name = m.group(3)
                player = Player(name=player_name)
                command = m.group(4)
                steamid = player.steamid

                if command == "set up lobby":
                    if player.authenticated:
                        try:
                            location = Location(name='lobby')
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
                            location = Location(owner=player, name='home')
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
                            tn_cmd.send_message(player_name + " believes to have died, but didn't oO")
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
                                finally:
                                    player.authenticated = True

                        else:
                            tn_cmd.send_message(player_name + " has entered a wrong password oO!")
                else:
                    tn_cmd.send_message("the command '" + command + "' is unknown to me :)")

            m = re.search(r"^(.+?) (.+?) INF GMSG: Player '(.*)' joined the game\r", response)
            if m:
                player_name = m.group(3)
                player = Player(name=player_name)
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
                        location = Location(name='lobby')
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
                        location = Location(name='lobby')
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
    mandatory thread! all other threads will be shut down if this one is missing  
    """
    telnet_observer_event = Event()
    telnet_observer_thread = TelnetObserverLoop(telnet_observer_event, TelnetCommand.get_connection(HOST, PORT, PASS))
    telnet_observer_thread.start()

    """
    optional threads. depend on global loop to be running
    it is the plan that they can inject chat listeners into the main loop
    this needs some planning, will be required before we start with big additions though 
    """
    player_poll_loop_event = Event()
    player_poll_loop_thread = PollPlayers(player_poll_loop_event, TelnetCommand.get_connection(HOST, PORT, PASS))
    player_poll_loop_thread.setDaemon(True)  # thread get's shut down when all non daemon threads have ended
    player_poll_loop_thread.start()

