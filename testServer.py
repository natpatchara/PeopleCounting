import cv2
import logging
import socketserver
from threading import Condition
from http import server
import cgi
import subprocess
import os

def reset():
    global p
    p.terminate()
    with open("result.txt","w") as f:
            f.write("0\n")
            f.write("0")
    p = subprocess.Popen(['python',path+'\pi_counter_server_alpha1.py'])

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            with open("index.html","r") as f:
                content = f.read()
            content = content.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            #print(self.rfile)
        elif self.path == "/cap.jpg":
            with open("cap.jpg","rb") as cap:
                content = cap.read()
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpg')
            self.send_header('Content-Disposition', 'attachment; filename="cap.jpg"')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/cap.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    frame = cv2.imread("cap.jpg")
                    try:
                        frame = cv2.imencode('.jpeg',frame)[1].tostring()
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                    except Exception as e:
                        pass
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
    
        else:
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        if self.path=="/send":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE':self.headers['Content-Type']})
            result = form["input"].value
            print("Input is " + result)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'input')
        elif self.path=="/get_image":
            with open("ShowImage.html","r") as f:
                content = f.read().encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path=="/get_count":
            with open("result.txt", "r") as f:
                data = f.readlines()
            for line in data:
                line = line.encode('utf-8')
            with open("CountResult.html","r") as f:
                content = f.read()
            content = content.format(Up = data[0],Down = data[1]).encode("utf-8")
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/reset':
            reset()            
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            with open("index.html","r") as f:
                content = f.read()
            content = content.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            
            
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

#vs = cv2.VideoCapture("output.avi")
try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    path = os.path.dirname(os.path.realpath(__file__))
    p = subprocess.Popen(['python',path+'\pi_counter_server_alpha1.py'])
    server.serve_forever()
finally:
    #vs.release()
    print("shutdown server")
    p.terminate()
           
