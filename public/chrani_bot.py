#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
from threading import Event
# these are the actual bot-modules :
from chrani_bot.setup import HOST, PORT, PASS
from chrani_bot.telnet_cmd import TelnetCommand
from chrani_bot.telnet_observer import TelnetObserver
from chrani_bot.poll_players import PollPlayers
import chrani_bot.rabaDB.Raba as Rc
import chrani_bot.rabaDB.fields as rf
# here come the actions
from chrani_bot.actions_lobby import actions_lobby
from chrani_bot.actions_backpack import actions_perks
from chrani_bot.actions_home import actions_home
from chrani_bot.tools import merge_dicts


class Player(Rc.Raba):
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


class Location(Rc.Raba):
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
    telnet_observer_thread.actions = merge_dicts(actions_lobby, actions_perks, actions_home)
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
