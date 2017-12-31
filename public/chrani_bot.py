#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
from threading import Event
import chrani_bot.rabaDB.Raba as Rc
import chrani_bot.rabaDB.fields as rf
# these are the actual bot-modules :
from chrani_bot.setup import setup_config_file, get_bot_config
from chrani_bot.telnet_cmd import TelnetCommand
# threads and observers
from chrani_bot.threads.telnet_actions import TelnetActions
from chrani_bot.threads.player_worker import PlayerWorker
from chrani_bot.threads.player_actions import PlayerActions
# here come the actions
from chrani_bot.actions.lobby import actions_lobby
from chrani_bot.actions.backpack import actions_perks
from chrani_bot.actions.home import actions_home
# here come the actions
from chrani_bot.observers.lobby import observers_lobby


if __name__ == '__main__':
    host, port, password = get_bot_config(
        setup_config_file(
            "../private/config.txt"),
        "dummy",  # dummy might be the local running test-server ^^
        "chrani_server"
    )

    HOST = host
    PORT = port
    PASS = password

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
        radius = rf.Primitive()

        def __init__(self):
            pass


    match_types = {
        'chat_commands': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF Chat: \'(?P<player_name>.*)\': /(?P<command>.+)\r",
        'telnet_events_player': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF GMSG: Player '(?P<player_name>.*)' (?P<command>.*)\r",
        'telnet_events_playerspawn': r"^(?P<datetime>.+?) (?P<stardate>.+?) INF PlayerSpawnedInWorld \(reason: (?P<command>.+?), .* PlayerName='(?P<player_name>.*)'\r"}

    """
    mandatory thread! all other threads will be shut down if this one is missing  
    """
    telnet_observer_event = Event()
    telnet_observer_thread = TelnetActions(telnet_observer_event, TelnetCommand(HOST, PORT, PASS), Player, Location)
    telnet_observer_thread.match_types = match_types
    telnet_observer_thread.actions = actions_lobby + actions_perks + actions_home
    telnet_observer_thread.start()

    """
    optional threads. depend on global loop to be running
    it is the plan that they can inject chat listeners into the main loop
    this needs some planning, will be required before we start with big additions though 
    """
    player_poll_loop_event = Event()
    player_poll_loop_thread = PlayerWorker(player_poll_loop_event, TelnetCommand(HOST, PORT, PASS), Player)
    player_poll_loop_thread.setDaemon(True)  # thread get's shut down when all non daemon threads have ended
    player_poll_loop_thread.start()

    player_observer_loop_event = Event()
    player_observer_loop_thread = PlayerActions(player_observer_loop_event, player_poll_loop_thread, TelnetCommand(HOST, PORT, PASS), Player, Location)
    player_observer_loop_thread.observers = observers_lobby
    player_observer_loop_thread.start()
