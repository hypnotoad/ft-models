#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
from TouchStyle import *
from ft_timing import *


class Worker(QObject):
    detection = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, ft_timer):
        super().__init__()
        self.ft_timer = ft_timer
        
        self.min_seconds = 1
        self.thresh=10000
        
    def run(self):
        self.prevlight = False
        self.ticks = 0
        self.started = None
        print("worker started")
        while not QThread.currentThread().isInterruptionRequested():
            # 15ms frequency of this loop
            state = self.ft_timer.step()
            light = state['value'] < self.thresh
            transition = self.prevlight and not light
            self.prevlight = light
            self.ticks += 1

            diff = None
            trigger = False
            if self.started:
                diff = state['time'] - self.started
                trigger =  transition and diff > self.min_seconds

            if trigger or self.ticks % 10 == 0:
                self.detection.emit({'diff': diff,
                                     'ticks': self.ticks,
                                     'trigger': trigger,
                                     'detected': light})

            if trigger or transition and not self.started:
                self.started = state['time']
                self.ticks = 0

        print("worker finished")
        self.tasks = []
        self.finished.emit()


class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        self.ft_timer = FtTiming(1)
        self.ft_thread = None
        self.best_timing = None

        # create the empty main window
        w = TouchWindow("Stopuhr")
        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        self.laserReceived = QCheckBox()
        self.laserReceived.setMaximumWidth(32)
        hbox.addWidget(self.laserReceived)
        
        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.on_startstop)
        hbox.addWidget(self.startButton)

        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.on_clear)
        hbox.addWidget(self.clearButton)
        
        self.currWidget = QLabel()
        vbox.addWidget(self.currWidget)
        
        self.prevWidget = QLabel()
        vbox.addWidget(self.prevWidget)

        self.bestWidget = QLabel()
        vbox.addWidget(self.bestWidget)

        self.on_clear()
        
        w.centralWidget.setLayout(vbox)
        w.show()

        self.exec()

    def on_startstop(self):
        if self.ft_thread:
            self.stop_thread()
            self.startButton.setText("Start")
        else:
            self.launch_thread()
            self.startButton.setText("Stop")

    def on_clear(self):
        self.best_timing = None
        self.currWidget.setText("not started")
        self.prevWidget.setText("no prev lap")
        self.bestWidget.setText("no best lap")
        
        
    def on_detection(self, event):
        #print(event)
        timing = event['diff']

        self.laserReceived.setChecked(event['detected'])
        
        if timing:
            self.currWidget.setText("curr %3.3f s" % timing)

        if not event['trigger']:
            return

        resolution = event['diff'] / event['ticks'] * 1000
        print("detection resolution: {} ms".format(resolution))

        self.prevWidget.setText("prev %3.3f s" % timing)

        if not self.best_timing or self.best_timing > timing:
            self.best_timing = timing
            self.bestWidget.setText("best %3.3f s" % event['diff'])
        


    def stop_thread(self):
        self.ft_thread.requestInterruption()
        self.ft_thread_old = self.ft_thread
        self.ft_thread = None

    def launch_thread(self):
        self.ft_thread = QThread()
        self.worker = Worker(self.ft_timer)

        self.worker.moveToThread(self.ft_thread)
        self.worker.detection.connect(self.on_detection)
        self.worker.finished.connect(self.ft_thread.quit)
        self.ft_thread.started.connect(self.worker.run)
        self.ft_thread.finished.connect(self.worker.deleteLater)
        self.ft_thread.finished.connect(self.ft_thread.deleteLater)

        self.ft_thread.start()


            
        
if __name__ == "__main__":

    FtcGuiApplication(sys.argv)

