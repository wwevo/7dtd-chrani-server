# 7dtd-chrani-server

**noob-coded python bot to control a 7 Days to Die game-server**

installation should be just a matter of installing python 2.7, dropping this script somewhere and execute it. do create
a passwords.txt file to configure your server, create a folder somewhere for the database. that should be it really 

this is in no way a fully functional bot. it's a work in progress. let's call it Early Access ^^

I will try to get this thing modular as much as possible, always depending on my current knowledge. the plan is to
really only have to use the functions desired and leave out all others if you wish. if you just want it to say hello
to new players it should only do things required to accomplish exactly that.

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

Listen to chat commands (*The main loop*)

    should run and do nothing else but timeout (if set up),
    listen to chat-commands and trigger their actions

The player-poll

    periodically scans for new players and stores the data in a sqlite3
    database 

together with player-positions and chat commands, we are free to develop bot-functions like conditional teleporting
and setting up a home-zone for example

**The following commands and actions are available at this time:**
* greeting new players, welcoming back old ones
* setting up a lobby (/set up lobby)
    * new players will get ported to the lobby location
    * a command will allow them to get sent back to their original spawn (/password <password>)
    * players will be ported back to the lobby after death if they haven't entered the password
* players can set up a home and port back there (/make this my home && /take me home)
* players can port back to their last place of death to retrieve their backpack (/man, where's my pack?)

this code only has some exception checking and also almost ZERO security / sanity checks. this is in NO WAY ready for
a public server.

code-base is tested on 100% vanilla server and one with Coppis + Botman. Not tested with any other mods.
also tested it with three instances of this bot connected to the same server by accident. it worked :) 

coppis will be needed though as a lot of important features won#t be available without it. like pm's and colored chat