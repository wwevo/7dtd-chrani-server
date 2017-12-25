#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
import ConfigParser  # only needed for fancy config import
from threading import Event
from rabaDB.rabaSetup import *
import rabaDB.Raba as R
import rabaDB.fields as rf
# these are the actual bot-modules :
from chrani_bot.telnet_cmd import TelnetCommand
from chrani_bot.telnet_observer import TelnetObserver
from chrani_bot.poll_players import PollPlayers

# import config options
# I like to keep them out of the way for the versioning system, a config file
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


if __name__ == '__main__':
    """
    mandatory thread! all other threads will be shut down if this one is missing  
    """
    telnet_observer_event = Event()
    telnet_observer_thread = TelnetObserver(telnet_observer_event, TelnetCommand(HOST, PORT, PASS), Player, Location)
    telnet_observer_thread.start()

    """
    optional threads. depend on global loop to be running
    it is the plan that they can inject chat listeners into the main loop
    this needs some planning, will be required before we start with big additions though 
    """
    player_poll_loop_event = Event()
    player_poll_loop_thread = PollPlayers(player_poll_loop_event, TelnetCommand(HOST, PORT, PASS), Player)
    player_poll_loop_thread.setDaemon(True)  # thread get's shut down when all non daemon threads have ended
    player_poll_loop_thread.start()
