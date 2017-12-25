#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys

# going to make heavy use of telnet and regexp
import telnetlib
import re

from threading import Timer,Thread,Event

class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

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

tn = telnetlib.Telnet(HOST, PORT)
# this is the exact prompt from the games telnet. it might change with a new game-version
tn.read_until("Please enter password:")
tn.write(PASS.encode('ascii') + b"\r\n")
# last 'welcome' line from the games telnet. it might change with a new game-version
line = tn.read_until("Press 'exit' to end session.")

# doing an output just for testing. the final script will not have a web interface
print(line)
print "<hr />"
print "Players"
print "<hr />"

# lp = list players
tn.write("lp" + b"\r\n")
output = tn.read_until(b"\r\n")
while output:
    print(output)
    output = tn.read_until(b"\r\n")
    # last line from the games lp command. it might change with a new game-version
    if re.match(r"Total of [\d]* in the game", output) is not None:
        print(output)
        break
print "<hr />"
print "Keystones"
print "<hr />"
# llp = list land protection
tn.write("llp" + b"\r\n")
output = tn.read_until(b"\r\n")
while output:
    print(output)
    output = tn.read_until(b"\r\n")
    # last line from the games llp command. it might change with a new game-version
    if re.match(r"Total of [\d]* keystones in the game", output) is not None:
        print(output)
        break
print "<hr />"
print "Command test"
print "<hr />"
# a small loop that waits until a timestamp preceeding the text 'INF' is found,
# a tag the game sets for informational log entries. This will need a timeout / exit
# of some sort
output = tn.read_until(b"\r\n")
while output:
    m = re.search(r"^(.+?) (.+?) INF", output)
    if m:
        timestamp_start = datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
        break
    output = tn.read_until(b"\r\n")

# the main loop
# can always be broken with an in-game chat command : /chrani stop test
# will also stop executing after a set (approximate) timeout if so desired
timeout = 25
while output:
    m = re.search(r"^(.+?) (.+?) INF", output)
    if m:
        timestamp_now = datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
        elapsed_time = timestamp_now - timestamp_start
        if elapsed_time.seconds >= timeout:
            print "command '/chrani stop test' was not used in the last " + str(elapsed_time.seconds) + " seconds. Timeout!!!"
            break
    if re.match(r"^(.+?) (.+?) INF Chat: \'.*\':.* \/chrani stop test", output) is not None:
        print(output)
        break
    output = tn.read_until(b"\r\n")

tn.close()
