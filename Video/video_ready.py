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
    name: None

    def do_POST(self):
        try:
            if self.path.startswith("/start"):
                if hasattr(Handler, 'process') and Handler.process is not None:
                    self.end_recording()
                self.start_recording()
                self.respond_with_body(200, {'status': 'video recording started', 'pid': Handler.process.pid})
                return
            if self.path.startswith("/end"):
                self.end_recording()
                self.respond_with_body(200, {'status': 'video recording ended'})
                return
            if self.path.startswith("/cancel"):
                self.cancel_recording()
                self.respond_with_body(200, {'status': 'video recording cancelled'})
                return
        except Exception as e:
            self.respond_with_body(500, {'exception': str(e)})

    def start_recording(self):
        query_components = parse_qs(urlparse(self.path).query)
        name = query_components["name"][0] if 'name' in query_components else "video"
        Handler.process = subprocess.Popen("/opt/bin/video.sh '" + name + "'", stdout=subprocess.PIPE,
                                           shell=True,
                                           preexec_fn=os.setsid)
        Handler.name = name

    def end_recording(self):
        os.killpg(os.getpgid(Handler.process.pid), signal.SIGTERM)
        Handler.process = None

    def respond_with_body(self, code, body):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode('utf-8'))

    def cancel_recording(self):
        os.killpg(os.getpgid(Handler.process.pid), signal.SIGTERM)
        Handler.process.wait()
        Handler.process = None
        os.remove("/videos/"+Handler.name)


httpd = HTTPServer(('0.0.0.0', video_ready_port), Handler)
httpd.serve_forever()
