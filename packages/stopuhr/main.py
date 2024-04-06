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
        self.ft_timer = ft_timer
        
    def run(self):
        self.prevdetection = False
        self.min_seconds = 1
        while QThread.currentThread().isInterruptionRequested():
            state = self.ft_timer.step()
            detection = state['value'] > 10000
            transition = detection and not self.prevdetection
            self.prevdetection = detection

            if self.started:
                diff = state['time'] - self.started
                self.currWidget.setText("%3.3f s" % diff)
        
            if not transition:
                continue
        
            if not self.started:
                self.started = state['time']
                continue

            if diff > self.min_seconds:
                self.started = state['time']
                self.stateWidget.setText("%3.3f s" % diff)
                continue

        print("worker finished")
        self.tasks = []
        self.finished.emit()


class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        self.ft_timer = FtTiming(4)
        self.started = None

        # create the empty main window
        w = TouchWindow("Stopuhr")
        vbox = QVBoxLayout()

        self.currWidget = QLabel()
        vbox.addWidget(self.currWidget)
        
        self.stateWidget = QLabel()
        vbox.addWidget(self.stateWidget)

        
        w.centralWidget.setLayout(vbox)
        w.show()
        self.exec_()

    def launch_thread(self, tasks):
        print("Launching thread with %d tasks" % len(tasks))
        # self.plotter_thread and self.worker are cleaned up by QT. That means
        # that we must never call launch_thread if a thread is still
        # running.
        if self.is_running:
            print("launch_thread called but running!")
            return
        self.is_running = True
        
        self.plotter_thread = QThread()
        self.worker = Worker(self.ft_timer)
        self.worker.set_tasks(tasks)
        self.worker.moveToThread(self.plotter_thread)
        
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.plotter_thread.quit)
        self.plotter_thread.started.connect(lambda: self.on_running(True))
        self.plotter_thread.started.connect(self.worker.run)
        self.plotter_thread.finished.connect(lambda: self.on_running(False))
        self.plotter_thread.finished.connect(self.worker.deleteLater)
        self.plotter_thread.finished.connect(self.plotter_thread.deleteLater)
        self.plotter_thread.finished.connect(lambda: print("plotter thread finished"))

        self.plotter_thread.start()
        print("plotter thread started")

            
        
if __name__ == "__main__":

    FtcGuiApplication(sys.argv)

