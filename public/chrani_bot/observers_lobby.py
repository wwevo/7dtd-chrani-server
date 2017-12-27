from rabaDB.filters import *

observers_lobby = []


def player_left_area(self, connection):
    try:
        location = self.Location(name='lobby')
    except KeyError:
        return

    f = RabaQuery(self.Player)
    f.addFilter(authenticated=None)

    center_x = float(location.pos_x)
    center_y = float(location.pos_z)
    radius = float(10)

    for player in f.run():
        if ((float(player.pos_x) - center_x) ** 2 + (float(player.pos_z) - center_y) ** 2 > radius ** 2):
            connection.send_message(connection.tn, "And stay there!")
            teleport_command = "teleportplayer " + player.steamid + " " + str(int(float(location.pos_x))) + " " + str(
                int(float(location.pos_y))) + " " + str(int(float(location.pos_z))) + "\r\n"
            print teleport_command
            # need to include a time comparison, no two teleports should happen within, say, two seconds
            connection.tn.write(teleport_command)


observers_lobby.append(("player left lobby", player_left_area, "(self, connection)"))


def player_approaching_boundary_from_inside(self, connection):
    try:
        location = self.Location(name='lobby')
    except KeyError:
        return

    f = RabaQuery(self.Player)
    f.addFilter(authenticated=None)
    if not f:
        return

    center_x = float(location.pos_x)
    center_y = float(location.pos_z)
    radius = float(7.5)

    for player in f.run():
        if not (float(player.pos_x) - center_x) ** 2 + (float(player.pos_z) - center_y) ** 2 > radius ** 2 and ((float(player.pos_x) - center_x) ** 2 + (float(player.pos_z) - center_y) ** 2 > (radius - 2.5) ** 2):
            connection.send_message(connection.tn, "get your ass back in the lobby or else")


observers_lobby.append(("player approaching boundary from inside", player_approaching_boundary_from_inside, "(self, connection)"))
