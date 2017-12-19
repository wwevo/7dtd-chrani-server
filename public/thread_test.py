#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# enable debugging
import cgitb
cgitb.enable()

print "Content-Type: text/plain;charset=utf-8"
print
print "Hello World!"

from  threading import Thread, Event

class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(0.5):
            print("my thread")
            # call a function

stopFlag = Event()
thread = MyThread(stopFlag)
thread.start()
# this will stop the timer
#stopFlag.set()