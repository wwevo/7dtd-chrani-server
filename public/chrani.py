#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# enable debugging
import cgitb
cgitb.enable()
# imports
import sys
import telnetlib
import re
import datetime 
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
tn = telnetlib.Telnet(HOST, PORT)

def setup_telnet_connection():
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
    list_players_response_raw = ""
    response = None
    tn.write("lp" + b"\r\n")
    while list_players_response_raw == "" or response:
        response = tn.read_until(b"\r\n")
        list_players_response_raw = list_players_response_raw + response

        if re.match(r"Total of [\d]* in the game", response) is not None:
            return list_players_response_raw
            break

def loop():
    """
    don't even know where to begin
    I'm throwing everything in here I can think of
    """
    timeout_start = None
    latest_timestamp = None
    timeout_in_seconds = 5
    response = None
    continued_telnet_log_raw = ""

    while continued_telnet_log_raw == "" or response:
        response = tn.read_until(b"\r\n")
        continued_telnet_log_raw = continued_telnet_log_raw + response
        """
        get a flowing timestamp going
        implement simple timeout function for debug and testing
        """
        m = re.search(r"^(.+?) (.+?) INF", response)
        if m:
            latest_timestamp = datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
            if timeout_in_seconds != 0:
                if timeout_start is None:
                    timeout_start = datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
                elapsed_time = latest_timestamp - timeout_start
                if elapsed_time.seconds >= timeout_in_seconds:
                    return continued_telnet_log_raw

        # group(1) = datetime, group(2) = stardate?, group(3) = bot command
        m = re.search(r"^(.+?) (.+?) INF Chat: \'.*\':.* \/chrani (.+)", response)
        if m:
            if m.group(3) == "stop test":
                return("test stopped!" + "<br />")
            elif m.group(3) == "say something nice":
                print "something nice!" + "<br />"
            elif m.group(3) == "say something bad":
                print "something bad!" + "<br />"
            else:
                print response + "<br />"

welcome_message_raw = setup_telnet_connection()
list_players_response_raw = list_players()
continued_telnet_log_raw = loop();
tn.close()

# doing an output just for testing. the final script will not have a web interface
print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<body>"
print welcome_message_raw
print list_players_response_raw
print continued_telnet_log_raw
print "</body>"
print "</html>"


