#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
cgitb.enable()

# going to make heavy use of telnet and regexp
import telnetlib
import re

# import variables
# i like to kee them out of the way for the verioning system, a config file
# seems to be a sensible way
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("../private/passwords.txt")
HOST = config.get("telnet", "telnet_host")
PORT = config.get("telnet", "telnet_port")
PASS = config.get("telnet", "telnet_pass")

print "Content-type:text/html\r\n\r\n"

tn = telnetlib.Telnet(HOST, PORT)
tn.read_until("Please enter password:")
tn.write(PASS.encode('ascii') + b"\r\n")

line = tn.read_until("Press 'exit' to end session.")

print "<html>"
print "<body>"
print(line)

print "<hr />"
print "Players"
print "<hr />"

tn.write("lp" + b"\r\n")
output = tn.read_until(b"\r\n")
while output:
    print(output)
    output = tn.read_until(b"\r\n")
    if re.match(r"Total of [\d]* in the game", output) is not None:
        print(output)
        break

print "<hr />"
print "Keystones"
print "<hr />"

tn.write("llp" + b"\r\n")
output = tn.read_until(b"\r\n")
while output:
    print(output)
    output = tn.read_until(b"\r\n")
    if re.match(r"Total of [\d]* keystones in the game", output) is not None:
        print(output)
        break

print "</body>"
print "</html>"

tn.close()