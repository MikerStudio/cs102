import asyncio
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


def translate_path(path):
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


def create_response(headers, body, protocol=''):
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

    response = ''
    code, message = body
    response += protocol + ' '
    response += str(code) + ' '
    response += responses[code][0] + "\r\n"

    if not 'Content-Length' in headers.keys():
        response += 'Content-Length: 0\r\n'

    for i in headers.keys():
        response += i + ': ' + headers[i] + "\r\n"

    response += 'Date: ' + datetime.now().strftime("%b %d %Y %H:%M:%S %Z") + '\r\n'
    response += 'Server: asyncio/python\r\n\r\n'

    response = response.encode('utf-8')
    if isinstance(message, str):
        response += message.encode('utf-8')
    else:
        response += message
    return response


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    response_headers = {}
    response_body = (200, '')

    print(f"Received {message!r} from {addr!r}")

    data = message.split('\r\n\r\n')
    headers = data[0].split('\r\n')
    if not '\r\n' in data[0]:
        response_body = (400, 'Bad Request')
        response_headers = {'Content-Length': str(len('Bad request'))}
        response = create_response(response_headers, response_body)
        writer.write(response)
        await writer.drain()
        return
    method = headers[0].split()[0]
    query = headers[0].split()[1]
    protocol = headers[0].split()[2]
    try:
        headers = dict([
            (i.split(':')[0],
             i.split(':')[1][1:])
            for i in headers[1:-1]])
    except:
        print()
        print('Error')
        print()
        response_body = (400, 'Bad Request')
        response_headers = {'Content-Length': str(len('Bad request'))}
        response = create_response(response_headers, response_body, protocol)
        writer.write(response)
        await writer.drain()
        return
    if len(data) > 1 and data[1] != '' or method == 'POST':
        response_body = (400, 'Bad Request')
        response_headers = {'Content-Length': str(len('Bad request'))}
        response = create_response(response_headers, response_body, protocol)
        writer.write(response)
        await writer.drain()
        return

    query, extension, index_key, image_key = translate_path(query)

    if extension == '.js':
        response_headers["Content-Type"] = "application/javascript"

    elif extension in ['.jpeg', '.jpg', '.png', '.gif']:
        if extension[1:] == 'jpg':
            response_headers["Content-Type"] = "image/jpeg"
        else:
            response_headers["Content-Type"] = "image/" + extension[1:]
        image_key = True

    else:
        response_headers["Content-Type"] = "text/" + extension[1:]

    try:
        if image_key:
            mode = 'rb'
        else:
            mode = 'r'
        with open(file=query, mode=mode) as f:
            data = f.read()
            if method != 'HEAD':
                response_body = (200, data)
            else:
                response_body = (200, '')
            response_headers["Content-Length"] = str(len(data))
    except FileNotFoundError:
        if index_key:
            response_body = (403, '')
        else:
            response_body = (404, '')
        response_headers["Content-Length"] = '0'
    response_headers["Connection"] = "close"

    response = create_response(response_headers, response_body, protocol)
    print(f"Send: {response!r}")
    writer.write(response)
    await writer.drain()

    print("Close the connection")
    writer.close()


async def main():
    server = await asyncio.start_server(
        handle_echo, '127.0.0.1', 9000)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


asyncio.run(main())
