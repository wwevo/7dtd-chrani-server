# 7dtd-chrani-server

**noob-coded python bot to control a 7 Days to Die game-server**

this is in no way a fully functional bot. it's a work in progress. let's call it Early Access ^^
it already works though. you could use it for your small private server to make life easier there, having home commands
and such. it survived a full day of running already. hasn't been tested on a larger server though, I have no idea what
will happen when the server lags or simply has a lot of players on.  

##installation
should be just a matter of installing python 2.7, dropping this script somewhere and execute it. do create
a passwords.txt file to configure your server, create a folder somewhere for the database. that should be it really

the only thing you need is any 7dtd dedicated server and a console with access to python. it will work with any 7dtd
server that has telnet enabled. no mods other than the Serverfixes and Coppi's are required for all the features.
slimmed down, you could run it on any server really, you won't have the hide commands feature for example, so everyone
could see what everyone else is typing :)   

##current state
*this is my very first project with python*, apart from the Hello World example, so a lot of stuff might take a lot of
time for me, and I will not always hit the best methods of doing things I'm sure. feel free to comment on my code or
even helping out with stuff.

this project is meant to benefit our 7 Days to Die Game-server and the Online-panel I am developing for it as well. all
decisions regarding this scripts future will have to be weighed against our needs first, so no feature requests
please :) If you do develop your own features based on this, I'd very much like to know about it, it will possibly help
me improving this bot!

I want all parts to be self-contained.

so far we have

Connect

    to the games telnet and authenticate

Send messages

    to the games chat

Listen and react to telnet lines / chat commands (*The main loop*)

    should run and do nothing else but timeout (if set up),
    listen to telnet lines / chat commands and trigger their actions
    a list of already available commands can be found further down
    write your own, it's easy!

The player-poll (background task)

    periodically scans for new players and stores the data in a sqlite3
    database

together with player-positions and chat commands, we are free to develop bot-functions like conditional teleporting
and setting up a home-zone for example

assuming you have installed the Serverfixes and Coppi's mod:

**here is a brief overview of what is working at this time**
* the bot says hello when it is started. in color!
* chat commands (anything start starts with /) will be supressed
 
**the following commands and actions are available at this time:**
* greeting new players, welcoming back old ones
* setting up a lobby (/set up lobby), and remove it again (/make the lobby go away)
    * new players will get ported to the lobby location
    * a command will allow them to get sent back to their original spawn (/password <password>)
    * players will be ported back to the lobby after death if they haven't entered the password
* players can set up a home and port back there (/make this my home && /take me home)
* players can port back to their last place of death to retrieve their backpack (/man, where's my pack?)

##known issues
this code only has some exception checking and also almost ZERO security / sanity checks. this is in NO WAY ready for
a public server. I think. I am not good at these things :)

the way I inject the bot's actions into the main loop is insufficient. I need a much more flexible/magical way. can't
even module out the password function cause it takes an extra parameter...

#will it run?
code-base is tested on
* a16.4 100% vanilla server 
* a16.4 server with Coppi's + Botman-Bot.
* tested it with three instances of this bot connected to the same server by accident 

##future
I will try to get this thing modular as much as possible, always depending on my current python knowledge. the plan is to
really only have to use the functions desired and leave out all others if you wish. if you just want it to say hello
to new players it should only do things required to accomplish exactly that.

I've started to refactor the hell out of the code to make it unit-testable. not there yet, but it's getting there.
I have also started on getting the functions out of the loop, to allow for dynamic loading of required / desired
functions -> this is almost done. I need a more elegant way though
