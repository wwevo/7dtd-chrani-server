# 7dtd-chrani-server

noob-coded python bot to control a 7 Days to Die gameserver


So even if this is not really useful at the moment, it might be a starting point for noob coders like me :)

I will try to get this thing modular as much as possible, always depending on my current knowledge

This is my very first project with python, so a lot of stuff might take a lot of time for me, and I will not always hit the best methods of doing things I'm sure :) Feel free to comment on my code or even helping out with stuff.

This project is meant to benefit our 7 Days to Die Gameserver and an the Online-panel I am developing for it as well. All decisions regarding this scripts future will have to be weighed against our needs first, so no feature requests please :) If you do develop your own features based on this, I'd very much like to know about it, it will possibly help me improving this bot!

I want all parts to be self-contained.

So far we have

Connect

    to the games telnet and authenticate

Send messages

    to the Games chat

Listen to chat commands (*The main loop*)

    should run and do nothing else but timeout (if set up) and listen to chat-commands 
    simplest of bots imaginable, could be used as an echo-bot or for really simple server-wide notifications


The player-poll

    should periodically scan for new players and do something with that data, storing it in a database for example, or just in memory, if we don't want to get fancy. 

Together with player-positions and chat commands, we are free to develop bot-functions like conditional teleporting and setting up a homezone

Code-base is tested on 100% vanilla server and one with Coppis + Botman. Not tested with any other mods.