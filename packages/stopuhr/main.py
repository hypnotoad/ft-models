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
        
    def run(self):
        self.prevlight = False
        self.ticks = 0
        self.started = None
        while not QThread.currentThread().isInterruptionRequested():
            state = self.ft_timer.step()
            light = state['value'] < 1000
            transition = self.prevlight and not light
            self.prevlight = light
            self.ticks += 1

            diff = None
            trigger = False
            if self.started:
                diff = state['time'] - self.started
                trigger =  transition and diff > self.min_seconds

            if trigger or self.ticks % 100 == 0:
                self.detection.emit({'diff': diff, 'ticks': self.ticks, 'trigger': trigger})

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

        self.currWidget = QLabel()
        vbox.addWidget(self.currWidget)
        
        self.prevWidget = QLabel()
        vbox.addWidget(self.prevWidget)

        self.bestWidget = QLabel()
        vbox.addWidget(self.bestWidget)

        w.centralWidget.setLayout(vbox)
        w.show()

        self.launch_thread()
        self.exec()
        self.stop_thread()

    def on_detection(self, event):
        print(event)
        timing = event['diff']
        self.currWidget.setText(("curr %3.3f s" % timing) if timing else "<not started>")

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

