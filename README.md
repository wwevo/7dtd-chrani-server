# 7dtd-chrani-server

**noob-coded python bot to control a 7 Days to Die game-server**

*(abandoned project, last change on jan 2018)*

    due to some misconceptions and spaghetti-code, I've ran into several walls. feel free to use this code as a starting
    point or whatever, a lot of stuff works already.
    I'm sure a seasoned programmer can salvage this pretty quickly ^^

    Based on my experiences with this, I will start fresh :)


this is only in some ways a functional bot. it's a work in progress. let's call it Early Access ^^
All functions it provides work, and they don't crash so far. You could use it up for your small private server to
make life easier there, having home commands and such. It has zero security measures against hackers and high latency
players. Yet. It should not be hard to write a ping kicker for example, all required data is available already

Please consider forking this project if you plan on extending on it, so others can benefit from your work as well  

## installation
should be just a matter of installing python 2.7, dropping this script somewhere and execute it. do create
a config.txt file to configure your server, create a folder somewhere for the database. that should be it really

the only thing you need is any 7dtd dedicated server and a console with access to python. it will work with any 7dtd
server that has telnet enabled. no mods other than the Serverfixes and Coppi's are required for all the features.
slimmed down, you could run it on any server really, you won't have the hide commands feature for example though, so everyone
could see what everyone else is typing :)   

## current state
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

Listen and react to telnet lines / chat commands (*The main loop*)

    should run and do nothing else but timeout (if set up),
    listen to telnet lines / chat commands and trigger their actions
    a list of already available commands can be found further down
    write your own, it's easy!

The player-poll (background task)

    periodically scans for new players and stores the data in a sqlite3
    database

The player-observer (background task)

    we know EVERYTHING ABOUT YOU!

Database (SQlite3)

    the database-handler (rabaDB) will take care of everything. You can edit the fields according to your modules
    needs and just go with it

together with player-positions and chat commands, we are free to develop bot-functions like conditional teleporting
and setting up a home-zone for example. with the new player-observer, we can do real time tracking of players,
keeping them in the lobby for example

assuming you have installed the Serverfixes and Coppi's mod:

**here is a brief overview of what is working at this time**
* the bot says hello when it is started. in color!
* chat commands (anything start starts with /) will be supressed
* the lobby, if it has been set, will keep unauthorized players inside,
  porting them back if they try to leave
 
**the following commands and actions are available at this time:**
* greeting new players, welcoming back old ones
* authorizing players with a password (/password <password>)
    * you can remove authentication by providing any password other than the actual password
* setting up a lobby (/set up lobby), and remove it again (/make the lobby go away)
    * you can set the radius of the lobby. It's a sphere, so it has height (/set up lobby perimeter)
    * new players will get ported to the lobby location
    * a command will allow them to get sent back to their original spawn (/password <password>)
    * players will be ported back to the lobby after death, if they haven't entered the password
    * players will be ported back to the lobby if they try to leave it, if they haven't entered the password
    * you can remove the lobby (/make the lobby go away)
* players can set up a home and port back there (/make this my home && /take me home)
* players can port back to their last place of death to retrieve their backpack (/man, where's my pack?)

### known issues
this code only has some exception checking and also almost ZERO security / sanity checks. this is in NO WAY ready for
a public server. I think. I am not good at these things :)

the way I inject the bot's actions into the main loop may be insufficient. I'd like a much more flexible/magical way.
It does work the they it should, but it looks like garbage ^^

### will it run?
code-base is tested on
* a16.4 100% vanilla server 
* a16.4 server with Coppi's + Botman-Bot (some command clashing, but it works)
* tested on a local windows install and Coppi's
* tested it with three instances of this bot connected to the same server by accident 

it survived a full day of running already. hasn't been tested on a larger server though, I have no idea what
will happen when the server lags or simply has a lot of players on.

the bot will stop working correctly if the server is reinitializing while the bot is running, like a restart for
example. 

## future
I will try to get/keep this thing modular as much as possible, always depending on my current python knowledge.
the plan is to really only have to use the functions desired and leave out all others if you wish. if you just
want it to say hello to new players it should only do things required to accomplish exactly that

I've started to refactor the hell out of the code to make it unit-testable. not there yet, but it's getting there.
I still struggle to understand unit-testing.
I have also started on getting the functions out of the loop, to allow for dynamic loading of required / desired
functions -> this is almost done. I might need a more elegant way though

the database fields have to be adjusted manually atm. I am looking for a way to make that modular as well, but it's
low priority at this time

the main goal of this bot is to make it a data provider for my 7dtd-chrani-panel, an online-map with special admin
features. I ran into several walls trying to integrate the Botman-bot and failed in the end, wgich actually motivated
me to start this bot :) 

since I am currently, effectively alone on this project, I have to work on all fronts at once. only way for me to do
it without losing interest altogether :)