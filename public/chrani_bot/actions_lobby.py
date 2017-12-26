actions_lobby = dict()


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


command = "set up lobby"
action = set_up_lobby
actions_lobby.update({command: action})


def on_respawn_after_death_lobby(self, player, connection):
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


command = "Died"
action = set_up_lobby
actions_lobby.update({command: action})
