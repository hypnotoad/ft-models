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
        
    def run(self):
        self.started = None
        self.prevlight = False
        self.min_seconds = 1
        self.ticks = 0
        while not QThread.currentThread().isInterruptionRequested():
            state = self.ft_timer.step()
            light = state['value'] < 1000
            transition = self.prevlight and not light
            self.prevlight = light
            self.ticks += 1

            if not transition:
                continue
        
            if not self.started:
                self.started = state['time']
                self.ticks = 0
                continue

            diff = state['time'] - self.started
            if diff < self.min_seconds:
                continue

            self.started = state['time']
            self.detection.emit({'diff': diff, 'ticks': self.ticks})
            continue

        print("worker finished")
        self.tasks = []
        self.finished.emit()


class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        self.ft_timer = FtTiming(1)

        # create the empty main window
        w = TouchWindow("Stopuhr")
        vbox = QVBoxLayout()

        self.currWidget = QLabel()
        vbox.addWidget(self.currWidget)
        
        self.stateWidget = QLabel()
        vbox.addWidget(self.stateWidget)

        w.centralWidget.setLayout(vbox)
        w.show()

        self.launch_thread()
        self.exec()
        self.stop_thread()

    def on_detection(self, event):
        resolution = event['diff'] / event['ticks'] * 1000
        print("detection resolution: {} ms".format(resolution))
        self.currWidget.setText("%3.3f s" % event['diff'])
        

    def stop_thread(self):
        self.ft_thread.requestInterruption()

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

