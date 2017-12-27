actions_perks = []


def on_player_death(self, player):
    """
    saves location of the last death for a later return
    :param player: player-object
    :return: nothing to return
    """
    try:
        location = self.Location(owner=player, name='backpack')
    except KeyError:
        location = self.Location()
        location.name = 'backpack'
        location.owner = player

    location.pos_x = player.pos_x
    location.pos_y = player.pos_y
    location.pos_z = player.pos_z
    location.save()


actions_perks.append(("isequal", "died", on_player_death, "(self, player,)"))


def on_respawn_after_death(self, player, connection):
    """
    states to authenticated players that they can port to their backpack
    :param player: player-object pulled from database
    :param connection: Telnet command object
    :return: nothing to return
    """
    if player.authenticated:
        connection.send_message(connection.tn, "type /man, where's my pack? in this chat to return to your backpack!")


actions_perks.append(("isequal", "Died", on_respawn_after_death, "(self, player, connection,)"))


def man_where_is_my_pack(self, player, connection):
    if player.authenticated:
        try:
            location = self.Location(owner=player, name='backpack')
            pos_x = location.pos_x
            pos_y = location.pos_y
            pos_z = location.pos_z
            teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
            # print teleport_command
            connection.tn.write(teleport_command)
            connection.send_message(connection.tn, player.name + " is laaaaazy :)")
        except KeyError:
            connection.send_message(connection.tn, player.name + " believes to have died, but didn't oO")
    else:
        connection.send_message(connection.tn, player.name + " needs to enter the password to get access to sweet commands!")


actions_perks.append(("isequal", "man, where's my pack?", man_where_is_my_pack, "(self, player, connection,)"))


