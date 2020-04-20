import argparse
import asynchat
import asyncore
import logging
import multiprocessing
import os
from datetime import datetime


def url_normalize(path):
    if path.startswith("."):
        path = "/" + path
    while "../" in path:
        p1 = path.find("/..")
        p2 = path.rfind("/", 0, p1)
        if p2 != -1:
            path = path[:p2] + path[p1 + 3:]
        else:
            path = path.replace("/..", "", 1)
    path = path.replace("/./", "/")
    path = path.replace("/.", "")
    return path


class FileProducer(object):

    def __init__(self, file, chunk_size=4096):
        self.file = file
        self.chunk_size = chunk_size

    def more(self):
        if self.file:
            data = self.file.read(self.chunk_size)
            if data:
                return data
            self.file.close()
            self.file = None
        return ""


class AsyncHTTPServer(asyncore.dispatcher):

    def __init__(self, host="127.0.0.1", port=9000):
        super().__init__()
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        AsyncHTTPRequestHandler(sock)


class AsyncHTTPRequestHandler(asynchat.async_chat):

    def __init__(self, sock):
        super().__init__(sock)
        self.data = None
        self.method = None
        self.query = None
        self.protocol = None
        self.sock = sock
        self.headers = {}
        self.response_body = ()
        self.response_headers = {}
        self.set_terminator(b"\r\n\r\n")

    def collect_incoming_data(self, data):
        data_not_parsed = data.decode('utf-8')
        if self.data is not None:
            self.parse_request()
        self.data = data_not_parsed
        self._collect_incoming_data(data)

    def found_terminator(self):
        self.parse_request()

    def parse_request(self):
        if self.headers == {}:
            headers_key = self.parse_headers()
            if not headers_key:
                self.send_error(400, 'Bad Request')
            if self.method == 'POST':
                if not ('Content-Length' in self.headers) or not (int(self.headers['Content-Length']) > 0):
                    self.handle_request()
            else:
                self.handle_request()
        else:
            self.handle_request()

    def parse_headers(self):
        headers = self.data.split('\r\n')
        try:
            self.headers = dict([(i.split(':')[0], i.split(':')[1][1:]) for i in headers[1:]])
            self.method = headers[0].split()[0]
            self.query = headers[0].split()[1]
            self.protocol = headers[0].split()[2]
        except:
            return False
        return True

    def handle_request(self):
        method_name = 'do_' + self.method
        if not hasattr(self, method_name):
            self.send_error(405)
            self.handle_close()
            return
        handler = getattr(self, method_name)
        handler()

    def send_error(self, code, message=None):
        try:
            short_msg, long_msg = self.responses[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg

        self.send_response(code, message)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Connection", "close")
        self.end_headers()

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def send_response(self, code, message=None):
        self.response_body = (code, message)
        return

    def end_headers(self):
        response = ''
        code, message = self.response_body
        response += self.protocol + ' '
        response += str(code) + ' '
        response += self.responses[code][0] + "\r\n"

        if not 'Content-Length' in self.response_headers.keys():
            response += 'Content-Length: 0\r\n'

        for i in self.response_headers.keys():
            response += i + ': ' + self.response_headers[i] + "\r\n"

        response += 'Date: ' + self.date_time_string() + '\r\n'
        response += 'Server: asyncio/python\r\n\r\n'

        response = response.encode('utf-8')
        if isinstance(message, str):
            response += message.encode('utf-8')
        else:
            response += message

        self.sock.sendall(response)

        return

    def date_time_string(self):
        return datetime.now().strftime("%b %d %Y %H:%M:%S %Z")

    def translate_path(self, path):
        query = 'files'
        query += path
        index_key = False
        image_key = False
        if query[-1] == '/':
            query += 'index.html'
            index_key = True
        query = url_normalize(query)
        if '?' in query:
            query = query[:query.find('?')]
        query = query.replace('%20', ' ')
        _, extension = os.path.splitext(query)
        return query, extension, index_key, image_key

    def do_GET(self, head=False):
        query, extension, index_key, image_key = self.translate_path(self.query)

        if extension == '.js':
            self.send_header("Content-Type", "application/javascript")

        elif extension in ['.jpeg', '.jpg', '.png', '.gif']:
            if extension[1:] == 'jpg':
                self.send_header("Content-Type", "image/jpeg")
            else:
                self.send_header("Content-Type", "image/" + extension[1:])
            image_key = True

        else:
            self.send_header("Content-Type", "text/" + extension[1:])

        try:
            if image_key:
                mode = 'rb'
            else:
                mode = 'r'
            with open(file=query, mode=mode) as f:
                data = f.read()
                if not head:
                    self.send_response(200, data)
                else:
                    self.send_response(200, '')
                self.send_header("Content-Length", str(len(data)))
        except FileNotFoundError:
            if index_key:
                self.send_response(403, '')
            else:
                self.send_response(404, '')
            self.send_header("Content-Length", '0')
        self.send_header("Connection", "close")
        self.end_headers()

    def do_HEAD(self):
        self.do_GET(True)

    responses = {
        200: ('OK', 'Request fulfilled, document follows'),
        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
    }


def parse_args():
    parser = argparse.ArgumentParser("Simple asynchronous web-server")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    parser.add_argument("--log", dest="loglevel", default="info")
    parser.add_argument("--logfile", dest="logfile", default='file.txt')
    parser.add_argument("-w", dest="nworkers", type=int, default=1)
    parser.add_argument("-r", dest="document_root", default=".")
    return parser.parse_args()


def run():
    server = AsyncHTTPServer(host=args.host, port=args.port)
    asyncore.loop()


if __name__ == "__main__":
    args = parse_args()

    logging.basicConfig(
        filename=args.logfile,
        level=getattr(logging, args.loglevel.upper()),
        format="%(name)s: %(process)d %(message)s")
    log = logging.getLogger(__name__)

    DOCUMENT_ROOT = args.document_root
    for _ in range(args.nworkers):
        p = multiprocessing.Process(target=run)
        p.start()
