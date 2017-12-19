#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
import sys
import telnetlib
import re
import time 
import ConfigParser

# begin main code ^^
# import config options
# I like to kee them out of the way for the versioning system, a config file
# seems to be a sensible way
config = ConfigParser.ConfigParser()
config.read("../private/passwords.txt")
HOST = config.get("telnet", "telnet_host")
PORT = config.get("telnet", "telnet_port")
PASS = config.get("telnet", "telnet_pass")

def setup_telnet_connection(tn):
    # this is the exact prompt from the games telnet. it might change with a new game-version
    password_prompt = tn.read_until("Please enter password:")
    tn.write(PASS.encode('ascii') + b"\r\n")
    # last 'welcome' line from the games telnet. it might change with a new game-version
    return tn.read_until("Press 'exit' to end session.")

def list_players():
    """
    fetches the response of the games telnet 'lp' command
    (lp = list players)
    last line from the games lp command, the one we are matching
    might change with a new game-version
    """
    tn = telnetlib.Telnet(HOST, PORT)
    setup_telnet_connection(tn)

    list_players_response_raw = ""
    response = None
    tn.write("lp" + b"\r\n")
    while list_players_response_raw == "" or response:
        response = tn.read_until(b"\r\n")
        list_players_response_raw = list_players_response_raw + response

        if re.match(r"Total of [\d]* in the game", response) is not None:
            return list_players_response_raw

def loop():
    """
    don't even know where to begin
    I'm throwing everything in here I can think of
    """
    tn = telnetlib.Telnet(HOST, PORT)
    setup_telnet_connection(tn)

    global global_loop
    global player_poll
    timeout_start = None
    latest_timestamp = None
    timeout_in_seconds = 10
    response = None
    continued_telnet_log_raw = ""

    while continued_telnet_log_raw == "" or response:
        response = tn.read_until(b"\r\n")
        continued_telnet_log_raw = continued_telnet_log_raw + response
        """
        get a flowing timestamp going
        implement simple timeout function for debug and testing
        """
        latest_timestamp = time.time()
        if timeout_in_seconds != 0:
            if timeout_start is None:
                timeout_start = time.time()
            elapsed_time = latest_timestamp - timeout_start
            print elapsed_time
            if elapsed_time >= timeout_in_seconds:
                """
                timeout occured. close the telnet, kill all threads, break the loop!
                """
                tn.close()
                global_loop.set()
                player_poll.set()
                break

        # group(1) = datetime, group(2) = stardate?, group(3) = bot command
        m = re.search(r"^(.+?) (.+?) INF Chat: \'.*\':.* \/chrani (.+)", response)
        if m:
            if m.group(3) == "stop test":
                print "test stopped!"
            elif m.group(3) == "say something nice":
                print "something nice!" + "<br />"
            elif m.group(3) == "say something bad":
                print "something bad!" + "<br />"
            else:
                print response + "<br />"

from  threading import Thread, Event
class PollPlayers(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(2):
            print list_players()
            # call a function

class GlobalLoop(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
            loop()

global_loop = Event()
global_loop_thread = GlobalLoop(global_loop)
global_loop_thread.start()

player_poll = Event()
player_poll_thread = PollPlayers(player_poll)
player_poll_thread.start()

