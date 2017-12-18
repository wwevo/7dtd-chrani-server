#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys

# enable debugging
import cgitb
cgitb.enable()

# going to make heavy use of telnet and regexp
import telnetlib
import re

# needed for timeout-functions
import datetime 

# import variables
# i like to kee them out of the way for the versioning system, a config file
# seems to be a sensible way
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("../private/passwords.txt")
HOST = config.get("telnet", "telnet_host")
PORT = config.get("telnet", "telnet_port")
PASS = config.get("telnet", "telnet_pass")

print "Content-type:text/html\r\n\r\n"

tn = telnetlib.Telnet(HOST, PORT)
# this is the exact prompt from the games telnet. it might change with a new game-version
tn.read_until("Please enter password:")
tn.write(PASS.encode('ascii') + b"\r\n")
# last 'welcome' line from the games telnet. it might change with a new game-version
welcome_message_raw = tn.read_until("Press 'exit' to end session.")

def list_players():
    list_players_response_raw = ""
    response = None
    tn.write("lp" + b"\r\n")
    while list_players_response_raw == "" or response:
        """
        lp = list players
        last line from the games lp command, the one we are matching
        might change with a new game-version
        """
        response = tn.read_until(b"\r\n")
        list_players_response_raw = list_players_response_raw + response
        if re.match(r"Total of [\d]* in the game", response) is not None:
            return list_players_response_raw
            break


def loop():
    timeout_start = None
    timeout_current = None
    timeout_max = 5
    response = None
    continued_telnet_log_raw = ""

    while continued_telnet_log_raw == "" or response:
        response = tn.read_until(b"\r\n")
        continued_telnet_log_raw = continued_telnet_log_raw + response
        if timeout_max != 0:
            m = re.search(r"^(.+?) (.+?) INF", response)
            if m:
                timeout_current = datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
                if timeout_start is None:
                    timeout_start = datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
                elapsed_time = timeout_current - timeout_start
                if elapsed_time.seconds >= timeout_max:
                    return("command '/chrani stop test' was not used in the last " + str(elapsed_time.seconds) + " seconds. Timeout!!!")

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

list_players_response_raw = list_players()
continued_telnet_log_raw = loop();
tn.close()

# doing an output just for testing. the final script will not have a web interface
print "<html>"
print "<body>"
print welcome_message_raw
print list_players_response_raw
print continued_telnet_log_raw
print "</body>"
print "</html>"


