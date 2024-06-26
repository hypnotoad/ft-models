#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import plotter
from TouchStyle import *
from PyQt5 import QtGui
import os
import math


def is_image(filename):
    return filename.endswith(".jpg")

def is_drawing(filename):
    return filename.endswith(".plt") or filename.endswith(".hpgl")

def create_preview(cmds, is_drawing, preview_size, preview_border, canvas_w, canvas_h):
    import preview_plotter

    plotter = preview_plotter.Plotter(width = canvas_w,
                                      height = canvas_h,
                                      border = preview_border,
                                      flip_x = not is_drawing,
                                      flip_y = is_drawing)
    for cmd in cmds:
        (cmd[1])(plotter)

    qimg = plotter.get_qt_preview(preview_size.width(), preview_size.height())
    return QPixmap.fromImage(qimg)


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    tasks = []

    def set_tasks(self, tasks):
        self.tasks = tasks

    def run(self):
        n_tasks = len(self.tasks)
        print("worker running with %d tasks" % n_tasks)
        update_rate = max([1, n_tasks // 200])
        for i in range(n_tasks):
            self.tasks[i]()
            if i % update_rate == 0:
                self.progress.emit(math.ceil(i / n_tasks * 100))
            if QThread.currentThread().isInterruptionRequested():
                break
        print("worker finished")
        self.tasks = []
        self.finished.emit()

class FtcGuiApplication(TouchApplication):

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
        self.worker = Worker()
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


    def on_running(self, running):
        print("on_running(%s)" % running)

        self.is_running = running
        self.update_buttons()


        
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        self.settings = QSettings('ftc', 'plotter')
        self.max_width = int(self.settings.value("max_width", 5000))
        self.max_height = int(self.settings.value("max_height", 3950))
        self.border = int(self.settings.value("border", 200))
        #um for 1k hpgl units. 1 hpgl unit should be 20um.
        self.mm_max_width = int(self.settings.value("mm_width", 100))
        
        self.datadir = os.path.dirname(__file__) + "/data/"
        self.cmds = []
        self.plotter = None
        self.is_running = False
        self.init_plotter()

        self.launch_thread([self.plotter.init])

        # create the empty main window
        w = TouchWindow("Plotter")
        vbox = QVBoxLayout()

        self.filename = ""

        self.preview = QLabel()
        s = self.preview.size()
        self.whitepix = QPixmap(s.width(), s.height())
        self.whitepix.fill()
        self.preview.setPixmap(self.whitepix)
        vbox.addWidget(self.preview)        

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        
        self.selectButton = QPushButton("Select")
        self.selectButton.clicked.connect(self.on_select)
        hbox.addWidget(self.selectButton)

        self.startStopButton = QPushButton("Start")
        self.startStopButton.clicked.connect(self.on_startstop)
        hbox.addWidget(self.startStopButton)

        self.q = QProgressBar()
        self.q.setOrientation(Qt.Horizontal)
        self.q.setMinimum(0)
        self.q.setMaximum(100)
        self.q.setTextVisible(False)
        self.q.setValue(0)
        self.q.setMaximumHeight(20)
        vbox.addWidget(self.q)

        menu = w.addMenu()
        menu_settings = menu.addAction("Settings")
        menu_settings.triggered.connect(self.on_settings)
        menu_calib = menu.addAction("Calibrate")
        menu_calib.triggered.connect(self.on_calibrate)
        
        self.update_buttons()

        w.centralWidget.setLayout(vbox)
        w.show()
        self.w=w

        if True:
            import upload

            self.webserver = QThread()
            self.upload_worker = upload.Worker()
            self.upload_worker.moveToThread(self.webserver)
            self.webserver.started.connect(self.upload_worker.run) 
            self.upload_worker.file_available.connect(self.on_file_uploaded)
            self.webserver.start()

        self.exec()

    def init_plotter(self):
        if os.path.isfile('/etc/fw-ver.txt'):
            self.plotter = plotter.Plotter('localhost', init=False)
        else:
            import dummy_plotter
            self.plotter = dummy_plotter.Plotter()

    def compute_ratio(self):
        # 1 hpgl unit should be 25um. Multipler==1 means that
        # max_width units are actually mm_max_width mm. So we need to
        # divide by that:
        hp_mm_s = 25/1000
        ft_mm_s = self.mm_max_width / self.max_width
        return hp_mm_s / ft_mm_s

    def on_file_uploaded(self, filename, drawing):
        print("file %s is available" % filename)

        self.filename = "<upload>"
        self.load_image(filename, drawing)
        self.loader.finished.connect(lambda x, y, filename=filename: os.remove(filename))

        
    def on_select(self):
        w = TouchDialog("Select File", self.w)
        vbox = QVBoxLayout()

        qlist = QListWidget()
        for file in os.listdir(self.datadir):
            if is_drawing(file) or is_image(file):
                qlist.addItem(file)
        qlist.sortItems(Qt.AscendingOrder)
        

        qlist.setSelectionMode(QAbstractItemView.SingleSelection)
        qlist.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        QScroller.grabGesture(qlist.viewport(), QScroller.LeftMouseButtonGesture);

        vbox.addWidget(qlist)

        w.centralWidget.setLayout(vbox)
        ret = w.exec()

        self.cmds = []
        self.update_buttons()
        self.preview.setPixmap(self.whitepix)

        if qlist.selectedItems():
            fn = qlist.selectedItems()[0].text()
            if is_drawing(fn) or is_image(fn):
                self.filename = fn
                self.load_image(self.datadir + fn)
                return

        # failure
        self.filename = ""


    def load_image(self, filename, drawing = None):

        self.popup = BusyAnimation(parent=self.w, timeout_s=30)
        self.popup.show()

        if drawing is None:
            drawing = is_drawing(filename)
        
        class Task(QObject):
            finished = pyqtSignal(object, object)
            def __init__(self, h, w, r, ps, border):
                QObject.__init__(self)
                self.max_height=h
                self.max_width=w
                self.ratio=r
                self.preview_size=ps
                self.border=border
            def run(self):
                if not drawing:
                    import edge
                    contours, tracer = edge.extract_contours(filename)
                        
                    cmds = tracer.plt_commands(contours,
                                                max_height=self.max_height,
                                                max_width=self.max_width,
                                                border=self.border)
                else:
                    cmds = plotter.plt_commands(filename,
                                                max_height=self.max_height,
                                                max_width=self.max_width,
                                                multiplier=self.ratio)

                pix = create_preview(cmds, drawing, preview_size = self.preview_size,
                                     preview_border = self.border,
                                     canvas_w = self.max_width, canvas_h = self.max_height)
                self.finished.emit(cmds, pix)

        self.loader_thread = QThread()
        self.loader = Task(self.max_height, self.max_width, self.compute_ratio(),
                           self.preview.size(), self.border)
        
        self.loader.moveToThread(self.loader_thread)
        self.loader.finished.connect(self.on_update_cmds)
        self.loader.finished.connect(self.loader_thread.quit)
        self.loader.finished.connect(self.loader.deleteLater)
        self.loader_thread.started.connect(self.loader.run)
        self.loader_thread.finished.connect(self.loader_thread.deleteLater)
        self.loader_thread.finished.connect(lambda: print("loader thread finished"))

        self.loader_thread.start()
        print("loader thread started")


    def on_update_cmds(self, cmds, pix):
        print("received %d cmds" % len(cmds))
        self.cmds = cmds
        self.on_progress(0)
        if self.popup:
            self.popup.close()
            self.popup.deleteLater()
            #self.popup = None ## this prevents that the animation is closed
        self.update_buttons()
        self.preview.setPixmap(pix)

    def update_buttons(self):
        self.startStopButton.setText("Stop" if self.is_running else "Start")
        self.startStopButton.setEnabled(len(self.cmds) != 0 and self.plotter is not None)
        #self.selectButton.setEnabled(not self.is_running)

    def on_startstop(self):
        if self.is_running:
            print("Stop")
            self.plotter_thread.requestInterruption()
        else:
            print("Start")
            tasks = [lambda cmd=cmd: (cmd[1])(self.plotter) for cmd in self.cmds]
            tasks.append(lambda p=self.plotter: p.home())
            self.launch_thread(tasks)

    def on_settings(self):
        w = TouchDialog("Settings", self.w)
        vbox = QVBoxLayout()

        def create_entry(name, cm): #init_val, cb):
            vbox.addWidget(QLabel(name))
            spin = QSpinBox(w)
            spin.setMinimum(1)
            spin.setMaximum(1000000)
            spin.setValue(getattr(self, cm))
            spin.valueChanged.connect(lambda i: setattr(self, cm, i))
            vbox.addWidget(spin)            
        
        create_entry("Max Width", "max_width")
        create_entry("Max Height", "max_height")
        create_entry("mm max width", "mm_max_width")
        
        w.centralWidget.setLayout(vbox)
        ret = w.exec()

        self.settings.setValue("max_width", self.max_width)
        self.settings.setValue("max_height", self.max_height)
        self.settings.setValue("mm_width", self.mm_max_width)
        self.settings.sync()

    def on_calibrate(self):
        if self.is_running:
            return
        
        tasks=[]
        tasks.append(lambda p=self.plotter: p.home())
        tasks.append(lambda p=self.plotter: p.pen(up=False))
        coords=((0, 0), (-self.max_width, 0, 0),
                (-self.max_width, self.max_height), (0, self.max_height),
                (0, 0))
        for c in coords:
            tasks.append(lambda c=c, p=self.plotter: p.go(c[0], c[1]))
        tasks.append(lambda p=self.plotter: p.pen(up=True))
        tasks.append(lambda p=self.plotter: p.home())
        self.launch_thread(tasks)
            
    def on_progress(self, progress: int):
        self.q.setValue(progress)
        
    
if __name__ == "__main__":

    FtcGuiApplication(sys.argv)
