import http.server
import pathlib


file_available = None

def set_file_available(signal):
    global file_available
    file_available = signal

class UploadHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(pathlib.Path(__file__).parent.resolve()), **kwargs)

    def do_GET(self):
        self.path = 'print.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path.startswith('/upload/'):
            def on_field(f):
                pass
            def on_file(f):
                import tempfile
                import shutil
                
                src = f.file_object
                src.seek(0)
                dst = tempfile.NamedTemporaryFile(delete=False)
                shutil.copyfileobj(src, dst)

                is_drawing = self.path.endswith('/hpgl')
                
                print("Saved upload as %s." % dst.name)
                
                if file_available:
                    file_available.emit(dst.name, is_drawing)
                # avoid that it gets deleted

            from thirdparty.multipart.multipart import multipart
            multipart.parse_form(self.headers, self.rfile, on_field, on_file)

        self.do_GET()
