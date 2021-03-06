import atexit
import telnetlib
import time
import re
from tools import timeout_occurred


class TelnetCommand:
    tn = None

    def __init__(self, telnet_host, telnet_port, telnet_pass):
        self.tn = TelnetCommand.get_connection(telnet_host, telnet_port, telnet_pass)
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.tn:
            self.tn.close()

    @staticmethod
    def get_connection(telnet_host, telnet_port, telnet_pass):
        """
        for now, until i know better, i want each part of this bot using
        their own telnet. i'm not actually sure if it works that way, but it seems
        like it ^^
        """
        connection = None
        while connection is None:
            try:
                connection = telnetlib.Telnet(telnet_host, telnet_port)
                TelnetCommand.authenticate(connection, telnet_pass)
                return connection
            except Exception, err:
                print "could not connect to the games telnet"
                time.sleep(4)

        return None

    @staticmethod
    def authenticate(connection, telnet_pass):
        # this is the exact prompt from the games telnet. it might change with a new game-version
        try:
            connection.read_until("Please enter password:")
            connection.write(telnet_pass.encode('ascii') + b"\r\n")
            # last 'welcome' line from the games telnet. it might change with a new game-version
            return connection.read_until("Press 'exit' to end session.")
        except:
            return False

    @staticmethod
    def send_message(connection, message):
        response = None
        send_message_response_raw = ""
        try:
            connection.write("say \"" + message + b"\"\r\n")
        except:
            return False

        # timeout_start = time.time()
        # while send_message_response_raw == "" or response and not timeout_occurred(2, timeout_start):
        #     response = connection.read_until(b"\r\n")
        #     send_message_response_raw = send_message_response_raw + response
        #
        #     if re.match(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + re.escape(re.sub(r"\[.*?\]", "", message)) + "\r", response) is not None:
        #         return True

    @staticmethod
    def teleport_player(connection, steamid, location):
        response = None
        teleport_player_response_raw = ""
        try:
            connection.write("teleportplayer " + steamid + " " + str(int(float(location.pos_x))) + " " + str(int(float(location.pos_y))) + " " + str(int(float(location.pos_z))) + b"\r\n")
        except:
            return False

        # timeout_start = time.time()
        # while send_message_response_raw == "" or response and not timeout_occurred(2, timeout_start):
        #     response = connection.read_until(b"\r\n")
        #     send_message_response_raw = send_message_response_raw + response
        #
        #     if re.match(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + re.escape(re.sub(r"\[.*?\]", "", message)) + "\r", response) is not None:
        #         return True

    @staticmethod
    def togglechatcommandhide(connection, prefix):
        response = None
        send_message_response_raw = ""
        command = "tcch " + prefix + b"\r\n"
        try:
            connection.write(command)
        except:
            return False

        # timeout_start = time.time()
        # while send_message_response_raw == "" or response and not timeout_occurred(2, timeout_start):
        #     response = connection.read_until(b"\r\n")
        #     send_message_response_raw = send_message_response_raw + response
        #
        #     if re.match(r"^Prefix \"" + prefix + "\" defined for chat commands\r", response) is not None:
        #         return True

