#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
import sys
import telnetlib
import re
import time 
import ConfigParser
from pprint import pprint

# begin main code ^^
# import config options
# I like to kee them out of the way for the versioning system, a config file
# seems to be a sensible way
config = ConfigParser.ConfigParser()
config.read("../private/passwords.txt")
bot_suffix = "_hoop"
HOST = config.get("telnet" + bot_suffix, "telnet_host")
PORT = config.get("telnet" + bot_suffix, "telnet_port")
PASS = config.get("telnet" + bot_suffix, "telnet_pass")

def setup_telnet_connection(tn):
    # this is the exact prompt from the games telnet. it might change with a new game-version
    password_prompt = tn.read_until("Please enter password:")
    tn.write(PASS.encode('ascii') + b"\r\n")
    # last 'welcome' line from the games telnet. it might change with a new game-version
    return tn.read_until("Press 'exit' to end session.")

send_message_tn = None
def send_message(message):
    global send_message_tn
    if send_message_tn is None:
        send_message_tn = telnetlib.Telnet(HOST, PORT)
        setup_telnet_connection(send_message_tn)
    response = None
    send_message_response_raw = ""

    send_message_tn.write("say \"" + message + b"\"\r\n")
    while send_message_response_raw == "" or response:
        response = send_message_tn.read_until(b"\r\n")
        send_message_response_raw = send_message_response_raw + response

        if re.match(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + message + "\r", response) is not None:
            return send_message_response_raw

from  threading import Thread, Event
class PollPlayers(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        """
        recorded the runtime of the poll, using it to calculate the exact wait
        time between executions
        """
        global list_players_response_time
        poll_frequency = 2
        next_poll = poll_frequency;
        while not self.stopped.wait(next_poll):
            next_poll = 2 - list_players_response_time
            print next_poll
            list_players()

list_players_tn = None
list_players_response_time = 0 # record the runtime of the entire poll
def list_players():
    """
    fetches the response of the games telnet 'lp' command
    (lp = list players)
    last line from the games lp command, the one we are matching
    might change with a new game-version
    """
    profile_timestamp_start = time.time()
    global list_players_tn
    global list_players_response_time
    if list_players_tn is None:
        list_players_tn = telnetlib.Telnet(HOST, PORT)
        setup_telnet_connection(list_players_tn)
    response = None
    list_players_response_raw = ""
    list_players_tn.write("lp" + b"\r\n")
    while list_players_response_raw == "" or response:
        response = list_players_tn.read_until(b"\r\n")
        list_players_response_raw = list_players_response_raw + response

        if re.match(r"Total of [\d]* in the game", response) is not None:
            list_players_response_time = time.time() - profile_timestamp_start
            # print "players polled"
            return list_players_response_raw

loop_tn = None
def loop():
    """
    don't even know where to begin
    I'm throwing everything in here I can think of
    """
    global loop_tn
    global global_loop
    global player_poll
    if loop_tn is None:
        loop_tn = telnetlib.Telnet(HOST, PORT)
        setup_telnet_connection(loop_tn)
    timeout_start = None
    latest_timestamp = None
    timeout_in_seconds = 0
    response = None
    continued_telnet_log_raw = ""
    while continued_telnet_log_raw == "" or response:
        response = loop_tn.read_until(b"\r\n")
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
            # print elapsed_time
            if elapsed_time >= timeout_in_seconds:
                """
                timeout occured. close the telnet, kill all threads, break the loop!
                """
                list_players_tn.close()
                loop_tn.close()
                global_loop.set()
                player_poll.set()
                break

        # group(1) = datetime, group(2) = stardate?, group(3) = bot command
        m = re.search(r"^(.+?) (.+?) INF Chat: \'.*\':.* \/chrani (.+)\r", response)
        if m:
            command = m.group(3)
            if command == "stop test":
                send_message(command + " received")
            elif command == "say something nice":
                send_message("something nice")
            elif command == "say something bad":
                send_message("something bad")
            else:
                send_message(command + " is unknown to me")

class GlobalLoop(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        loop()


class StorePlayerList(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        return
        # send_message("stored")


global_loop = Event()
global_loop_thread = GlobalLoop(global_loop)
global_loop_thread.start()

player_poll = Event()
player_poll_thread = PollPlayers(player_poll)
player_poll_thread.start()

store_player_list = Event()
store_player_list_thread = StorePlayerList(store_player_list)
store_player_list_thread.start()

