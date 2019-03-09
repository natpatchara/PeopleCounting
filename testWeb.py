import cv2
import logging
import socketserver
from threading import Condition
from http import server
import cgi
import os
import time

PAGE="""\
<html>
<head>
<title>Python Test Video Recorder</title>
</head>
<body>
<center><h1>Python Test Video Server</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
<form method="post" action="/{act}">
<input type="submit" value="{val}"/>
</form>
</body>
</html>
"""

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.format(act="record",val="start-reording").encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            #print(self.rfile)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    ret, frame = vs.read()
                    frame = cv2.imencode('.jpeg',frame)[1].tostring()
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/example.mp4':
            try:
                file = open("example.mp4", "rb")
                stat = os.fstat(file.fileno())
                length = stat.st_size

                self.send_response(200)
                self.send_header("Content-type", "video/mp4")
                self.send_header("Content-Length", length)
                self.send_header('Content-Disposition', 'attachment; filename="cap.mp4"')
                self.send_header("Accept-Ranges", "bytes")
                self.send_header(
                    "Last-Modified",
                    time.strftime(
                        "%a %d %b %Y %H:%M:%S GMT",
                        time.localtime(os.path.getmtime("example.mp4"))
                    )
                )
                self.end_headers()

                while True:
                    
                    data = file.read(80 * 1024)
                    if not data:
                        break
                    self.wfile.write(data)

            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
            
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        if self.path=="/record":
            content = PAGE.format(act='save',val='stop_recording').encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            self.send_response(200)
            self.end_headers()
        if self.path=="/save":
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    ret, frame = vs.read()
                    frame = cv2.imencode('.jpeg',frame)[1].tostring()
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

vs = cv2.VideoCapture(0)
try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    vs.release()
           
