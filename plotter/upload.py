import http.server
import socketserver
import pathlib
import tempfile
import shutil
from PyQt5 import QtCore
from thirdparty.multipart.multipart import multipart


class Worker(QtCore.QObject):
    file_available = QtCore.pyqtSignal(str)
    
    def run(self):
        serve_forever()


class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(pathlib.Path(__file__).parent.resolve()), **kwargs)
        
    def do_GET(self):
        self.path = 'print.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/verify':
            def on_field(f):
                pass
            def on_file(f):
                src = f.file_object
                src.seek(0)
                dst = tempfile.NamedTemporaryFile(delete=False)
                shutil.copyfileobj(src, dst)

                
                print("Saved upload as %s." % dst.name)
                worker.file_available.emit(dst.name)
                # avoid that it gets deleted

            multipart.parse_form(self.headers, self.rfile, on_field, on_file)

        self.do_GET()



        
def serve_forever(host="", port=8000):
    my_server = socketserver.TCPServer((host, port), UploadHandler)
    my_server.serve_forever()


# this object connects to the outside world with a signal
worker = Worker()


if __name__ == "__main__":
    if False:
        serve_forever()
    else:
        thread = QtCore.QThread()
        worker.moveToThread(thread)
        thread.start()
        thread.started.connect(worker.run) 
        worker.file_available.connect(lambda x: print("file %s is available" % x))

        app = QtCore.QCoreApplication([])
        app.exec()
