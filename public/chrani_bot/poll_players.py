
import re
from threading import Thread, Event
from rabaDB.rabaSetup import *
import atexit


class PollPlayers(Thread):
    tn_cmd = None
    tn = None
    poll_frequency = 2
    poll_players_response_time = 0  # record the runtime of the entire poll

    class PlayerList(Thread):
        """
        I've put this in here cause it's never gonna be needed
        outside of PollPlayers.
        """
        poll_players_raw = None
        poll_players_array = None

        def __init__(self, event, list_players_raw, player):
            self.Player = player
            Thread.__init__(self)
            self.stopped = event
            self.poll_players_raw = list_players_raw

        def run(self):
            self.update(self.poll_players_raw)
            self.stopped.set()

        def update(self, poll_players_raw):
            player_line_regexp = r"\d{1,2}. id=(\d+), ([\w+]+), pos=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), rot=\((.?\d+.\d), (.?\d+.\d), (.?\d+.\d)\), remote=(\w+), health=(\d+), deaths=(\d+), zombies=(\d+), players=(\d+), score=(\d+), level=(\d+), steamid=(\d+), ip=(\d+\.\d+\.\d+\.\d+), ping=(\d+)\n*"
            for m in re.finditer(player_line_regexp, poll_players_raw):
                """
                m.group(16) = steamid
                """
                try:
                    player = self.Player(steamid=m.group(16))
                except KeyError:
                    player = self.Player()

                player.id = m.group(1)
                player.name = m.group(2)
                player.pos_x = m.group(3)
                player.pos_y = m.group(4)
                player.pos_z = m.group(5)
                player.rot_x = m.group(6)
                player.rot_y = m.group(7)
                player.rot_z = m.group(8)
                player.remote = m.group(9)
                player.health = m.group(10)
                player.deaths = m.group(11)
                player.zombies = m.group(12)
                player.players = m.group(13)
                player.score = m.group(14)
                player.level = m.group(15)
                player.steamid = m.group(16)
                player.ip = m.group(17)
                player.ping = m.group(18)
                player.save()

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
        next_poll = 0
        while not self.stopped.wait(next_poll):
            """
            basically an endless loop
            fresh player-data is about the most important thing for this bot :)
            """
            list_players_raw, player_count = self.poll_players()

            # not sure if this is the way to go, but I wanted to have this in it's own thread so the time spend in the
            # actual server-transaction won't be delayed
            store_player_list_event = Event()
            store_player_list_thread = self.PlayerList(store_player_list_event, list_players_raw, self.Player)
            store_player_list_thread.start()
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

