import ConfigParser  # only needed for fancy config import
from rabaDB.rabaSetup import *


def setup_config_file(config_file):
    config = ConfigParser.ConfigParser()
    try:
        config.read(config_file)
    except:
        pass

    return config


def get_bot_config(config, bot_name="dummy", namespace="chrani_server"):
    try:
        host = config.get("telnet_" + bot_name, "telnet_host")
        port = config.get("telnet_" + bot_name, "telnet_port")
        password = config.get("telnet_" + bot_name, "telnet_pass")
    except:
        pass

    RabaConfiguration(namespace, '../private/db/' + bot_name + '.db')
    return host, port, password
