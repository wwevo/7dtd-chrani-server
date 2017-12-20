#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
import telnetlib
import re
import time 
import ConfigParser # only needed for fancy config import

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
    """
    for now, until i know better, i want each part of this bot using
    their own telnet. i'm not actually sure if it works that way, but it seems
    like it ^^
    """
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
    class StorePlayerList(Thread):
        def __init__(self, event):
            Thread.__init__(self)
            self.stopped = event

        def run(self):
            self.db_store_player_list()
            self.stopped.set()

        def db_store_player_list(self):
            """
            this will come later
            for now we can do it in memory
            """
            #print "player list stored"
            return

    poll_frequency = 2
    list_players_tn = None
    list_players_response_time = 0 # record the runtime of the entire poll

    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def __del__(self):
        if self.list_players_tn: self.list_players_tn.close()


    def run(self):
        """
        recorded the runtime of the poll, using it to calculate the exact wait
        time between executions
        """
        next_poll = self.poll_frequency;
        while not self.stopped.wait(next_poll):
            """
            basically an endless loop
            fresh playerdata is about the most important thing for this bot :)
            """
            next_poll = 2 - self.list_players_response_time
            print next_poll
            self.list_players()

            store_player_list = Event()
            store_player_list_thread = self.StorePlayerList(store_player_list)
            store_player_list_thread.start()

    def list_players(self):
        """
        fetches the response of the games telnet 'lp' command
        (lp = list players)
        last line from the games lp command, the one we are matching,
        might change with a new game-version
        """
        profile_timestamp_start = time.time()
        if self.list_players_tn is None:
            self.list_players_tn = telnetlib.Telnet(HOST, PORT)
            setup_telnet_connection(self.list_players_tn)
        response = None
        list_players_response_raw = ""
        self.list_players_tn.write("lp" + b"\r\n")
        while list_players_response_raw == "" or response:
            response = self.list_players_tn.read_until(b"\r\n")
            list_players_response_raw = list_players_response_raw + response

            if re.match(r"Total of [\d]* in the game", response) is not None:
                self.list_players_response_time = time.time() - profile_timestamp_start
                # print "players polled"
                return list_players_response_raw

class GlobalLoop(Thread):
    loop_tn = None
    timeout_in_seconds = 10

    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def __del__(self):
        if self.loop_tn: self.loop_tn.close()

    def run(self):
        self.loop()
        self.stopped.set()

    def loop(self):
        """
        don't even know where to begin
        I'm throwing everything in here I can think of
        """
        global player_poll
        if self.loop_tn is None:
            self.loop_tn = telnetlib.Telnet(HOST, PORT)
            setup_telnet_connection(self.loop_tn)

        timeout_start = None
        latest_timestamp = None
        response = None
        while response is None or response:
            response = self.loop_tn.read_until(b"\r\n", 5)
            """
            get a flowing timestamp going
            implement simple timeout function for debug and testing
            """
            latest_timestamp = time.time()
            if self.timeout_in_seconds != 0:
                if timeout_start is None:
                    timeout_start = time.time()
                elapsed_time = latest_timestamp - timeout_start
                # print elapsed_time
                if elapsed_time >= self.timeout_in_seconds:
                    """
                    no idea if this is really neccessary...
                    don't know where to close the thread otherwise
                    """
                    player_poll.set()
                    if send_message_tn: send_message_tn.close()
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

global_loop_thread = GlobalLoop(Event())
global_loop_thread.start()

player_poll_thread = PollPlayers(Event())
player_poll_thread.start()

