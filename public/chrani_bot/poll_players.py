
import re
from threading import Thread, Event
from rabaDB.rabaSetup import *
import atexit


class PollPlayers(Thread):
    tn_cmd = None
    tn = None
    poll_frequency = 2
    poll_players_response_time = 0  # record the runtime of the entire poll
    online_players = {}

    class PlayerData(Thread):
        """
        Does nothing but convert the given lp response from the games telnet (poll_players_raw) and
        saving that to various datasources / providers
        """
        poll_players_raw = None
        poll_players_array = None
        online_players = {}
        online_player = []

        def __init__(self, event, list_players_raw, player):
            self.Player = player
            Thread.__init__(self)
            self.stopped = event
            self.poll_players_raw = list_players_raw

        def run(self):
            self.update(self.poll_players_raw)
            self.stopped.set()

        @staticmethod
        def lp_response_raw_to_dict(poll_players_raw):
            online_players_dict = {}
            player_line_regexp = r"\d{1,2}. id=(\d+), ([\w+]+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\n*"
            for m in re.finditer(player_line_regexp, poll_players_raw):
                """
                m.group(16) = steamid
                """
                online_players_dict.update({m.group(16): {
                    "id": m.group(1),
                    "name": m.group(2),
                    "pos_x": m.group(3),
                    "pos_y": m.group(4),
                    "pos_z": m.group(5),
                    "rot_x": m.group(6),
                    "rot_y": m.group(7),
                    "rot_z": m.group(8),
                    "remote": m.group(9),
                    "health": m.group(10),
                    "deaths": m.group(11),
                    "zombies": m.group(12),
                    "players": m.group(13),
                    "score": m.group(14),
                    "level": m.group(15),
                    "steamid": m.group(16),
                    "ip": m.group(17),
                    "ping": m.group(18),
                    "authenticated": None
                }})
            return online_players_dict

        def save_dict_to_db(self, online_players):
            for steamid, online_player in online_players.iteritems():
                """
                m.group(16) = steamid
                """
                try:
                    player = self.Player(steamid=steamid)
                except KeyError:
                    player = self.Player()

                player.id = online_player["id"]
                player.name = online_player["name"]
                player.pos_x = online_player["pos_x"]
                player.pos_y = online_player["pos_y"]
                player.pos_z = online_player["pos_z"]
                player.rot_x = online_player["rot_x"]
                player.rot_y = online_player["rot_y"]
                player.rot_z = online_player["rot_z"]
                player.remote = online_player["remote"]
                player.health = online_player["health"]
                player.deaths = online_player["deaths"]
                player.zombies = online_player["zombies"]
                player.players = online_player["players"]
                player.score = online_player["score"]
                player.level = online_player["level"]
                player.steamid = online_player["steamid"]
                player.ip = online_player["ip"]
                player.ping = online_player["ping"]
                # self.online_players[steamid].update({"authenticated": player.authenticated})
                #player.save()

        def update(self, poll_players_raw):
            """
            updates both the db (could perhaps be optimized with a transaction, commiting all sets
            in one go instead of one by one in the loop) and the new dictionary available through the
            playerdata player_poll_loop_thread, containing the same data for currently online players as the db
            this should make database usage in "modules" unnecessary for currently online players, which should be
            the grunt of it really. I suppose most bot functions we want concern only currently online-players :)
            :param poll_players_raw:
            :return:
            :alters: player_poll_loop_thread.online_players
            """
            self.online_players = self.lp_response_raw_to_dict(poll_players_raw)  # "local copy"
            self.save_dict_to_db(self.online_players)  # store in db. We might only want to do this every x cycle

    def __init__(self, event, tn, player):
        self.tn_cmd = tn
        self.tn = self.tn_cmd.tn
        self.Player = player
        Thread.__init__(self)
        self.stopped = event
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.tn:
            self.tn.close()
        print "poll-players loop has been shut down"

    def run(self):
        """
        recorded the runtime of the poll, using it to calculate the exact wait
        time between executions
        """
        print "poll-players loop is ready and listening"
        next_poll = 0  # first poll need not wait darling!
        while not self.stopped.wait(next_poll):
            """
            basically an endless loop
            fresh player-data is about the most important thing for this bot :)
            """
            list_players_raw, player_count = self.poll_players()

            # not sure if this is the way to go, but I wanted to have this in it's own thread so the time spend in the
            # actual server-transaction won't be delayed
            store_player_list_event = Event()
            store_player_list_thread = self.PlayerData(store_player_list_event, list_players_raw, self.Player)
            store_player_list_thread.start()
            store_player_list_thread.join()  # dang, took me two hours to find out this is needed ^^
            self.online_players = store_player_list_thread.online_players
            next_poll = self.poll_frequency - self.poll_players_response_time
            print "player-data poll is active ({0} players, {1} bytes received, response-time: {2} seconds)".format(str(player_count), str(len(list_players_raw)), str(round(self.poll_players_response_time, 3)).ljust(5, '0'))

    def poll_players(self):
        """
        polls live player data from the games telnet
        times the action to allow for more accurate wait time
        returns complete telnet output and player count
        """
        profile_timestamp_start = time.time()

        list_players_response_raw = ""
        try:
            self.tn.write("lp" + b"\r\n")
            while list_players_response_raw == "" or response:
                """
                fetches the response of the games telnet 'lp' command
                (lp = list players)
                last line from the games lp command, the one we are matching,
                might change with a new game-version
                """
                response = self.tn.read_until(b"\r\n")
                list_players_response_raw = list_players_response_raw + response

                m = re.search(r"^Total of (\d{1,2}) in the game\r\n", response)
                if m:
                    player_count = m.group(1)
                    self.poll_players_response_time = time.time() - profile_timestamp_start
                    return list_players_response_raw, player_count
        except:
            return None, None

