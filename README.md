# 7dtd-chrani-server

noob-coded python bot to control a 7 Days to Die gameserver.

installation should be just a matter of installing python 2.7, dropping this script somewhere and execute it. do create a passwords.txt file to configure your server. that shuld be it really 

so even if this is not really useful at the moment, it might be a starting point for noob coders like me :)

I will try to get this thing modular as much as possible, always depending on my current knowledge. the plan is to really only have to use the functions desired and leave out all others if you wish. if you just want it to say hello to new players it should only do things required to accomplish exactly that.

this is my very first project with python, apart from the Hello World example, so a lot of stuff might take a lot of time for me, and I will not always hit the best methods of doing things I'm sure. feel free to comment on my code or even helping out with stuff.

this project is meant to benefit our 7 Days to Die Gameserver and the Online-panel I am developing for it as well. all decisions regarding this scripts future will have to be weighed against our needs first, so no feature requests please :) If you do develop your own features based on this, I'd very much like to know about it, it will possibly help me improving this bot!

I want all parts to be self-contained.

so far we have

Connect

    to the games telnet and authenticate

Send messages

    to the Games chat

Listen to chat commands (*The main loop*)

    should run and do nothing else but timeout (if set up)
    and listen to chat-commands
    simplest of bots imaginable, could be used as an echo-bot
    or for really simple server-wide notifications
    for now we have the '/make this my home' command and the
    'take me home' command. you can guess what they do ^^
    I have added a very experimental lobby and password check
    to get you out of the lobby again

The player-poll

    periodically scans for new players and stores the data in a sqlite3
    database 

together with player-positions and chat commands, we are free to develop bot-functions like conditional teleporting and setting up a homezone

this code has almost NO exception checking and also almost ZERO security / sanity checks. this is in NO WAY ready for a public server.

code-base is tested on 100% vanilla server and one with Coppis + Botman. Not tested with any other mods.
