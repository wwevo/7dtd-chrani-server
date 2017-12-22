#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# imports
import telnetlib
import re
import time 
import math
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



def fun(d, mime_type):
    reverse_linked_q = list()
    reverse_linked_q.append((list(), d))
    while reverse_linked_q:
        this_key_chain, this_v = reverse_linked_q.pop()
        # finish search if found the mime type
        if this_v == mime_type:
            return this_key_chain
        # not found. keep searching
        # queue dicts for checking / ignore anything that's not a dict
        try:
            items = this_v.items()
        except AttributeError:
            continue  # this was not a nested dict. ignore it
        for k, v in items:
            reverse_linked_q.append((this_key_chain + [k], v))
    # if we haven't returned by this point, we've exhausted all the contents
    raise KeyError

playerlist = {}
playerlocations = {}

from  threading import Thread, Event
class PollPlayers(Thread):
    poll_frequency = 2
    list_players_tn = None
    list_players_response_time = 0 # record the runtime of the entire poll

    class PlayerList(Thread):
        """
        I've put this in here cause it's never gonna be needed
        outside of PollPlayers.
        """
        list_players_raw = None
        list_players_array = None
        def __init__(self, event, list_players_raw):
            Thread.__init__(self)
            self.stopped = event
            self.list_players_raw = list_players_raw

        def run(self):
            self.save(self.list_players_raw)
            self.stopped.set()

        def save(self, list_players_raw):
            """
            this will come later
            for now we can do it in memory
            """
            global playerlist
            list_players_dict = self.convert_raw_playerdata(list_players_raw)
            playerlist.update(list_players_dict)
            return

        def convert_raw_playerdata(self, list_players_raw):
            list_players_dict = {}
            playerlines_regexp = r"\d{1,2}. id=(\d+), ([\w+]+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\n*"
            for m in re.finditer(playerlines_regexp, list_players_raw):
                """
                m.group(16) = steamid
                """
                list_players_dict[m.group(16)] = {"id": m.group(1), "name": m.group(2), "pos": {"x": m.group(3), "y": m.group(4), "z": m.group(5)}, "rot": {"1": m.group(6), "2": m.group(6), "3": m.group(6)}, "remote": m.group(9), "health": m.group(10), "deaths": m.group(11), "zombies": m.group(12), "players": m.group(13), "score": m.group(14), "level": m.group(15), "steamid": m.group(16), "ip": m.group(17), "ping": m.group(18)}

            return list_players_dict

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
        next_poll = 0;
        while not self.stopped.wait(next_poll):
            """
            basically an endless loop
            fresh playerdata is about the most important thing for this bot :)
            """
            next_poll = self.poll_frequency - self.list_players_response_time
            # print next_poll
            list_players_raw = self.poll_players()
            print "poll playerdata loop is alive"

            store_player_list_event = Event()
            store_player_list_thread = self.PlayerList(store_player_list_event, list_players_raw)
            store_player_list_thread.start()

    def poll_players(self):
        """
        
        """
        profile_timestamp_start = time.time()
        if self.list_players_tn is None:
            self.list_players_tn = telnetlib.Telnet(HOST, PORT)
            setup_telnet_connection(self.list_players_tn)

        list_players_response_raw = ""
        self.list_players_tn.write("lp" + b"\r\n")
        while list_players_response_raw == "" or response:
            """
            fetches the response of the games telnet 'lp' command
            (lp = list players)
            last line from the games lp command, the one we are matching,
            might change with a new game-version
            """
            response = self.list_players_tn.read_until(b"\r\n")
            list_players_response_raw = list_players_response_raw + response

            if re.match(r"Total of [\d]* in the game", response) is not None:
                self.list_players_response_time = time.time() - profile_timestamp_start
                return list_players_response_raw

class GlobalLoop(Thread):
    loop_tn = None
    timeout_in_seconds = 0

    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def __del__(self):
        if self.loop_tn: self.loop_tn.close()

    def run(self):
        """
        don't even know where to begin
        I'm throwing everything in here I can think of
        the plan is to have this loop execute periodically to scan for new
        telnet-lines issued by the game. for now I will hardcode most things,
        eventually all functions should be modules that can dynamically link
        into the loop somehow
        """
        player_poll_loop_event = Event()
        player_poll_loop_thread = PollPlayers(player_poll_loop_event)
        player_poll_loop_thread.start()

        global playerlist # contains current playerdata
        global playerlocations
        if self.loop_tn is None:
            self.loop_tn = telnetlib.Telnet(HOST, PORT)
            setup_telnet_connection(self.loop_tn)

        timeout_start = None
        while not self.stopped.wait(0.5):
            response = self.loop_tn.read_until(b"\r\n", 2)
            # print "global loop is alive"
            # print response
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
                    if statement, cause the eventit might not be present
                    """
                    if player_poll_loop_event is not None: player_poll_loop_event.set()
                    if send_message_tn: send_message_tn.close()
                    break

            # group(1) = datetime, group(2) = stardate?, group(3) = bot command
            m = re.search(r"^(.+?) (.+?) INF Chat: \'(.*)\': \/(.+)\r", response)
            # match specific chat messages
            if m:
                player = m.group(3)
                command = m.group(4)
                steamid = fun(playerlist, player)[0]
                if command == "make this my home":
                    homeX = playerlist[steamid]['pos']['x']
                    homeY = playerlist[steamid]['pos']['y']
                    homeZ = playerlist[steamid]['pos']['z']
                    playerlocations[steamid] = {}
                    playerlocations[steamid]['homePos'] = {}
                    playerlocations[steamid]['homePos']['x'] = homeX
                    playerlocations[steamid]['homePos']['y'] = homeY
                    playerlocations[steamid]['homePos']['z'] = homeZ
                    send_message(player + " has decided to settle down!")
                elif command == "take me home":
                    homeX = int(float(playerlocations[steamid]['homePos']['x']))
                    homeY = int(float(playerlocations[steamid]['homePos']['y']))
                    homeZ = int(float(playerlocations[steamid]['homePos']['z']))
                    teleport_command = "teleportplayer " + steamid + " " + str(homeX) + " " + str(homeY) + " " + str(homeZ) + "\r\n"
                    #print teleport_command
                    self.loop_tn.write(teleport_command)
                    send_message(player + " got homesick")
                elif command.startswith("password "):
                    p = re.search(r"password (.+)", command)
                    if p:
                        password = p.group(1)
                        print response
                        if password == "letmein":
                            print "correct password!!"
                            spawnX = int(float(playerlocations[steamid]['spawnPos']['x']))
                            spawnY = int(float(playerlocations[steamid]['spawnPos']['y']))
                            spawnZ = int(float(playerlocations[steamid]['spawnPos']['z']))
                            teleport_command = "teleportplayer " + steamid + " " + str(spawnX) + " " + str(spawnY) + " " + str(spawnZ) + "\r\n"
                            print teleport_command
                            # self.loop_tn.write(teleport_command)
                else:
                    send_message("the command '" + command + "' is unknown to me...")
            m = re.search(r"^(.+?) (.+?) INF GMSG: Player '(.*)' joined the game\r", response)
            if m:
                player = m.group(3)
                steamid = fun(playerlist, player)[0]
                homeX = playerlist[steamid]['pos']['x']
                homeY = playerlist[steamid]['pos']['y']
                homeZ = playerlist[steamid]['pos']['z']
                playerlocations[steamid] = {}
                playerlocations[steamid]['spawnPos'] = {}
                playerlocations[steamid]['spawnPos']['x'] = homeX
                playerlocations[steamid]['spawnPos']['y'] = homeY
                playerlocations[steamid]['spawnPos']['z'] = homeZ
                send_message("this servers bot says Hi to " + player + " o/")
                # send_message("your ass will be ported to our safe-zone until you have entered the password")
                # send_message("enter the password with /password <password> in chat")
                teleport_command = "teleportplayer " + steamid + " " + str(-888) + " " + str(-1) + " " + str(154) + "\r\n"
                print teleport_command
                # self.loop_tn.write(teleport_command)
        self.stopped.set()

global_loop_event = Event()
global_loop_thread = GlobalLoop(global_loop_event)
global_loop_thread.start()

