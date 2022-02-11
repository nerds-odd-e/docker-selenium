import json
import os
import signal
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import environ
from urllib.parse import urlparse, parse_qs

video_ready_port = int(environ.get('VIDEO_READY_PORT', 9000))


class Handler(BaseHTTPRequestHandler):
    process: None

    def do_POST(self):
        try:
            if self.path.startswith("/start"):
                query_components = parse_qs(urlparse(self.path).query)
                name = query_components["name"][0] if 'name' in query_components else "video"
                Handler.process = subprocess.Popen("/opt/bin/video.sh '" + name + "'", stdout=subprocess.PIPE,
                                                   shell=True,
                                                   preexec_fn=os.setsid)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(
                    json.dumps({'status': 'video recording started', 'pid': Handler.process.pid}).encode('utf-8'))
                return
            if self.path.startswith("/end"):
                os.killpg(os.getpgid(Handler.process.pid), signal.SIGTERM)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'video recording ended'}).encode('utf-8'))
                return
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'exception': str(e)}).encode('utf-8'))


httpd = HTTPServer(('0.0.0.0', video_ready_port), Handler)
httpd.serve_forever()
