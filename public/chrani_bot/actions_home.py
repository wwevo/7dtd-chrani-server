from tools import Dictlist

actions_home = Dictlist()


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
    try:
        location = self.Location(owner=player, name='spawn')
        connection.send_message(connection.tn, "Welcome back " + player.name + " o/")
    except KeyError:
        location = self.Location()
        location.name = 'spawn'
        location.owner = player
        location.pos_x = player.pos_x
        location.pos_y = player.pos_y
        location.pos_z = player.pos_z
        location.save()
        connection.send_message(connection.tn, "this servers bot says Hi to " + player.name + " o/")


actions_home["joined the game"] = on_player_join


def make_this_my_home(self, player, connection):
    if player.authenticated:
        try:
            location = self.Location(owner=player, name='home')
        except KeyError:
            location = self.Location()
            location.name = 'home'
            location.owner = player

        location.pos_x = player.pos_x
        location.pos_y = player.pos_y
        location.pos_z = player.pos_z
        location.save()

        connection.send_message(connection.tn, player.name + " has decided to settle down!")
    else:
        connection.send_message(connection.tn, player.name + " needs to enter the password to get access to sweet commands!")


actions_home["make this my home"] = make_this_my_home


def take_me_home(self, player, connection):
    if player.authenticated:
        try:
            location = self.Location(owner=player, name='home')
            pos_x = location.pos_x
            pos_y = location.pos_y
            pos_z = location.pos_z
            teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(pos_x))) + " " + str(
                int(float(pos_y))) + " " + str(int(float(pos_z))) + "\r\n"
            # print teleport_command
            connection.tn.write(teleport_command)
            connection.send_message(connection.tn, player.name + " got homesick")
        except KeyError:
            connection.send_message(connection.tn, player.name + " is apparently homeless...")
    else:
        connection.send_message(connection.tn,
                                player.name + " needs to enter the password to get access to sweet commands!")


actions_home["take me home"] = take_me_home
