import math

observers_lobby = []


def player_left_area(self, connection):
    try:
        location = self.Location(name='lobby')
        try:
            radius = float(location.radius)
        except AttributeError:
            radius = 10
    except KeyError:
        return

    online_players = self.player_poll_loop_thread.online_players
    for steamid, player in online_players.iteritems():
        print player
        try:
            # player = self.Player(steamid=steamid)
            if player["authenticated"] != 1:
                distance_to_lobby_center = float(math.sqrt(
                        (float(location.pos_x) - float(player["pos_x"])) ** 2 + (
                            float(location.pos_y) - float(player["pos_y"])) ** 2 + (
                            float(location.pos_z) - float(player["pos_z"])) ** 2))

                if distance_to_lobby_center > radius:
                    connection.send_message(connection.tn, "And stay there!")
                    teleport_command = "teleportplayer " + steamid + " " + str(
                        int(float(location.pos_x))) + " " + str(
                        int(float(location.pos_y))) + " " + str(int(float(location.pos_z))) + "\r\n"
                    print teleport_command
                    # need to include a time comparison, no two teleports should happen within, say, two seconds
                    connection.tn.write(teleport_command)
        except KeyError:
            return


observers_lobby.append(("player left lobby", player_left_area, "(self, connection)"))


def player_approaching_boundary_from_inside(self, connection):
    try:
        location = self.Location(name='lobby')
        try:
            radius = float(location.radius)
        except AttributeError:
            radius = 10
    except KeyError:
        return

    online_players = self.player_poll_loop_thread.online_players
    for steamid, player in online_players.iteritems():
        try:
            # player = self.Player(steamid=steamid)
            if player["authenticated"] != 1:
                distance_to_lobby_center = float(math.sqrt(
                        (float(location.pos_x) - float(player["pos_x"])) ** 2 + (
                            float(location.pos_y) - float(player["pos_y"])) ** 2 + (
                            float(location.pos_z) - float(player["pos_z"])) ** 2))

                if distance_to_lobby_center >= (radius / 2) and distance_to_lobby_center <= radius:
                    connection.send_message(connection.tn, "get your ass back in the lobby or else")
        except KeyError:
            return


observers_lobby.append(("player approaching boundary from inside", player_approaching_boundary_from_inside, "(self, connection)"))
