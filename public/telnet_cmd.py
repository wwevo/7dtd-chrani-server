import atexit
import telnetlib
import time
import re


class TelnetCommand:
    command_tn = None

    def __init__(self, telnet_host, telnet_port, telnet_pass):
        self.command_tn = TelnetCommand.get_connection(telnet_host, telnet_port, telnet_pass)
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.command_tn: self.command_tn.close()
        print "TelnetCommands telnet connection has been closed"

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
        connection.read_until("Please enter password:")
        connection.write(telnet_pass.encode('ascii') + b"\r\n")
        # last 'welcome' line from the games telnet. it might change with a new game-version
        return connection.read_until("Press 'exit' to end session.")

    def send_message(self, message):
        response = None
        send_message_response_raw = ""

        self.command_tn.write("say \"" + message + b"\"\r\n")
        while send_message_response_raw == "" or response:
            response = self.command_tn.read_until(b"\r\n")
            send_message_response_raw = send_message_response_raw + response

            if re.match(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + re.escape(message) + "\r", response) is not None:
                return send_message_response_raw

    def send_private_message(self, player, message):
        response = None
        send_message_response_raw = ""

        self.command_tn.write("say \"" + message + b"\"\r\n")

        while send_message_response_raw == "" or response:
            response = self.command_tn.read_until(b"\r\n")
            send_message_response_raw = send_message_response_raw + response

            if re.match(r"^(.+?) (.+?) INF Chat: \'.*\':.* " + re.escape(message) + "\r", response) is not None:
                return send_message_response_raw
