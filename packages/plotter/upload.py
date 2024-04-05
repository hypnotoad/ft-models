import socketserver
from PyQt5 import QtCore


# this class connects to the outside world with a signal
class Worker(QtCore.QObject):
    file_available = QtCore.pyqtSignal(str, bool)
    
    host=""
    port=8000

    def run(self):
        print("Web server starting")

        import upload_handler

        upload_handler.set_file_available(self.file_available)
        my_server = socketserver.TCPServer((self.host, self.port), upload_handler.UploadHandler)
        my_server.serve_forever()





if __name__ == "__main__":
    thread = QtCore.QThread()
    worker = Worker()
    worker.moveToThread(thread)
    thread.start()
    thread.started.connect(worker.run) 
    worker.file_available.connect(lambda x: print("file %s is available" % x))

    app = QtCore.QCoreApplication([])
    app.exec()
