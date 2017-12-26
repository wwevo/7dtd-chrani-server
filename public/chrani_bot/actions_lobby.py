from tools import Dictlist

actions_lobby = Dictlist()


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
        location.save()

        connection.send_message(connection.tn, player.name + " has set up a lobby. Good job!")
    else:
        connection.send_message(connection.tn,
                                player.name + " needs to enter the password to get access to sweet commands!")


actions_lobby["set up lobby"] = set_up_lobby


def on_player_join(self, player, connection):
    """
    ever newly logged in player will be handled here
    players will be greeted, a spawn will be set for new players
    if the player is not authenticated, he will be ported to the lobby, if one is set
    a prompt to enter the password will be displayed to unlock commands
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


actions_lobby["joined the game"] = on_player_join


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


actions_lobby["Died"] = on_respawn_after_death

