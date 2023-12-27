#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import gestensensor
from TouchStyle import *


class FtcGuiApplication(TouchApplication):

    def __init__(self, args):
        TouchApplication.__init__(self, args)

        self.exec()

        
    
if __name__ == "__main__":

    FtcGuiApplication(sys.argv)
