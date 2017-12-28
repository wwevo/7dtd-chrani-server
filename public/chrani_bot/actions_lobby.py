import math
import re

actions_lobby = []


def set_up_lobby(self, player, connection):
    if player.authenticated:
        try:
            location = self.Location(name='lobby')
        except KeyError:
            location = self.Location()
            location.name = 'lobby'

        location.pos_x = player.pos_x
        location.pos_y = player.pos_y
        location.pos_z = player.pos_z
        location.radius = 10
        location.save()

        connection.send_message(connection.tn, player.name + " has set up a lobby. Good job! set up the perimeter (default is 10 blocks) with /set up lobby perimeter, while standing on the edge of it.")
    else:
        connection.send_message(connection.tn,
                                player.name + " needs to enter the password to get access to sweet commands!")


actions_lobby.append(("isequal", "set up lobby", set_up_lobby, "(self, player, connection)"))


def set_up_lobby_perimeter(self, player, connection):
    if player.authenticated:
        try:
            location = self.Location(name='lobby')
        except KeyError:
            location = self.Location()
            location.name = 'lobby'

        location.radius = float(
            math.sqrt(
                (float(location.pos_x) - float(player.pos_x)) ** 2 + (float(location.pos_y) - float(player.pos_y)) ** 2 + (float(location.pos_z) - float(player.pos_z)) ** 2)
            )

        location.save()

        connection.send_message(connection.tn, player.name + " lobby ends here!")
    else:
        connection.send_message(connection.tn,
                                player.name + " needs to enter the password to get access to sweet commands!")


actions_lobby.append(("isequal", "set up lobby perimeter", set_up_lobby_perimeter, "(self, player, connection)"))


def remove_lobby(self, player, connection):
    if player.authenticated:
        try:
            location = self.Location(name='lobby')
            location.delete()
            connection.send_message(connection.tn, player.name + " said: Lobby, Be Gone!")
        except KeyError:
            connection.send_message(connection.tn, " no loby found oO")
    else:
        connection.send_message(connection.tn, player.name + " needs to enter the password to get access to sweet commands!")


actions_lobby.append(("isequal", "make the lobby go away", remove_lobby, "(self, player, connection)"))


def on_player_join(self, player, connection):
    """
    if the player is not authenticated, he will be ported to the lobby, if one is set
    a prompt to enter the password will be displayed on how to unlock commands otherwise
    :param player: player-object pulled from database
    :param connection: Telnet command object
    :return: nothing to return
    """
    if not player.authenticated:
        try:
            location = self.Location(name='lobby')
            pos_x = location.pos_x
            pos_y = location.pos_y
            pos_z = location.pos_z
            connection.send_message(connection.tn,
                                    "yo ass will be ported to our lobby plus tha command-shit is restricted yo")
            connection.send_message(connection.tn, "read the rules on https://chrani.net/rules")
            connection.send_message(connection.tn, "enter the password with /password <password> in this chat")
            teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(
                int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
            print teleport_command
            connection.tn.write(teleport_command)
        except KeyError:
            connection.send_message(connection.tn, "your account is restricted until you have read the rules")
            connection.send_message(connection.tn, "read the rules on https://chrani.net/rules")
            connection.send_message(connection.tn, "enter the password with /password <password> in this chat")


actions_lobby.append(("isequal", "joined the game", on_player_join, "(self, player, connection)"))


def on_respawn_after_death(self, player, connection):
    """
    sends players who are not authenticated back to the lobby
    :param self: needed for the class it will be running in
    :param player: player-object pulled from database
    :param connection: Telnet command object
    :return: nothing to return
    """
    if not player.authenticated:
        try:
            location = self.Location(name='lobby')
            pos_x = location.pos_x
            pos_y = location.pos_y
            pos_z = location.pos_z
            teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
            # print teleport_command
            self.tn.write(teleport_command)
            connection.send_message(connection.tn, "there is no escape from the lobby!")
        except KeyError:
            pass


actions_lobby.append(("isequal", "Died", on_respawn_after_death, "(self, player, connection)"))


def password(self, player, command, connection):
    p = re.search(r"password (.+)", command)
    if p:
        password = p.group(1)
        if password == "openup":
            # print "correct password!!"
            if not player.authenticated:
                try:
                    location = self.Location(name='lobby')
                    try:
                        location = self.Location(owner=player, name='spawn')
                        pos_x = location.pos_x
                        pos_y = location.pos_y
                        pos_z = location.pos_z
                        teleport_command = "teleportplayer " + player.steamid + " " + str(
                            int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
                        print teleport_command
                        connection.tn.write(teleport_command)
                        location.delete()
                    except KeyError:
                        connection.send_message(connection.tn, player.name + " has no place of origin it seems")
                except KeyError:
                    pass


actions_lobby.append(("startswith", "password", password, "(self, player, command, connection,)"))
