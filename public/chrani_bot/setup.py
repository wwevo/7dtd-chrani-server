import ConfigParser  # only needed for fancy config import
from rabaDB.rabaSetup import *

config = ConfigParser.ConfigParser()
config.read("../private/passwords.txt")

bot_suffix = "hoop"
HOST = config.get("telnet_" + bot_suffix, "telnet_host")
PORT = config.get("telnet_" + bot_suffix, "telnet_port")
PASS = config.get("telnet_" + bot_suffix, "telnet_pass")

RabaConfiguration('chrani_server', '../private/db/' + bot_suffix + '.db')
