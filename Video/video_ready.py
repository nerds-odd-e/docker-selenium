from http.server import BaseHTTPRequestHandler,HTTPServer
from os import environ
import json
import psutil
import subprocess
import os
import signal

video_ready_port = int(environ.get('VIDEO_READY_PORT', 9000))

class Handler(BaseHTTPRequestHandler):
    process: None

    def do_POST(self):
        try:
            if self.path == "/start":
                Handler.process = subprocess.Popen("/opt/bin/video.sh", stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'video recording started', 'pid': Handler.process.pid}).encode('utf-8'))
                return
            if self.path == "/end":
                os.killpg(os.getpgid(Handler.process.pid), signal.SIGTERM)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'video recording ended'}).encode('utf-8'))
                return
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'exception': str(e)}).encode('utf-8'))

httpd = HTTPServer( ('0.0.0.0', video_ready_port), Handler )
httpd.serve_forever()
