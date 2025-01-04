#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
from TouchStyle import *
#from subprocess import Popen, call, PIPE, check_output, CalledProcessError
import sys
import subprocess

SCRIPT = "/opt/fischertechnik/start-txtcontrol"


class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        w = TouchWindow("ROBO Server")
        print("initializing")
        
        vbox = QVBoxLayout()
        vbox.setSpacing(0)

        vbox.addStretch()

        self.enabled = QCheckBox("running")
        self.enabled.setCheckState(1) # Qt.PartiallyChecked
        self.enabled.toggled.connect(self.toggle_service)
        vbox.addWidget(self.enabled)

        
        vbox.addStretch()

        w.centralWidget.setLayout(vbox)

        self.start_timer = QTimer(self)
        self.start_timer.timeout.connect(self.check_service)
        self.start_timer.setSingleShot(True)
        self.start_timer.start(1000)

        w.show()
        self.exec_()

    def toggle_service(self, enabled):
        if enabled:
            self.start_service()
        else:
            self.stop_service()
    
    def start_service(self):
        print("starting service")
        subprocess.Popen(["sudo", SCRIPT, "start-service"])
        self.enabled.setCheckState(2) # Qt.Checked

    def stop_service(self):
        print("stopping service")
        subprocess.Popen(["sudo", SCRIPT, "stop-service"])
        self.enabled.setCheckState(0) # Qt.Unchecked
            
    def check_service(self):
        try:
            subprocess.check_output(["pidof", "TxtControlMain"])
            print("service is running")
            self.enabled.setCheckState(2) # Qt.Checked
            
        except subprocess.CalledProcessError:
            print("service is not running")
            self.enabled.setCheckState(0) # Qt.Unchecked

        
if __name__ == "__main__":
    print("launching...")
    FtcGuiApplication(sys.argv)

