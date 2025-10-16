from io import BytesIO
from Errors import CommandError, DisconnectError, Error

class ProtocolHandler(object):
    def __init__(self):
        # Redis/RESP3-like protocol
        self.handlers = {
            b'+': self.handle_simple_string,
            b'-': self.handle_error,
            b':': self.handle_integer,
            b'$': self.handle_string,
            b'*': self.handle_array,
            b'%': self.handle_dict,
            b'#': self.handle_boolean
        }

    def handle_request(self, socket_file):
        first_byte = socket_file.read(1)
        if not first_byte:
            raise DisconnectError()
        handler = self.handlers.get(first_byte)
        if not handler:
            raise ValueError(f"Unknown protocol type: {first_byte!r} check documentation for more info")
        return handler(socket_file)

    def handle_simple_string(self, socket_file):
        return socket_file.readline().rstrip(b'\r\n')

    def handle_error(self, socket_file):
        return socket_file.readline().rstrip(b'\r\n')

    def handle_integer(self, socket_file):
        return int(socket_file.readline().rstrip(b'\r\n'))

    def handle_string(self, socket_file):
        length = int(socket_file.readline().rstrip(b'\r\n'))
        if length == -1:
            return None
        data = socket_file.read(length + 2)[:-2]
        return data.decode('utf-8')

    def handle_array(self, socket_file):
        length = int(socket_file.readline().rstrip(b'\r\n'))
        if length == -1:
            return None
        return [self.handle_request(socket_file) for _ in range(length)]

    def handle_dict(self, socket_file):
        length = int(socket_file.readline().rstrip(b'\r\n'))
        if length == -1:
            return None
        elements = [self.handle_request(socket_file) for _ in range(length * 2)]
        return dict(zip(elements[::2], elements[1::2]))

    def handle_boolean(self, socket_file):
        val = socket_file.readline().rstrip(b'\r\n')
        return val == b't'

    def write_response(self, socket_file, response):
        buf = BytesIO()
        self._write(buf, response)
        buf.seek(0)
        socket_file.write(buf.getvalue())
        socket_file.flush()

    def _write(self, buf, data):
        if isinstance(data, str):
            buf.write(f"${len(data)}\r\n{data}\r\n".encode('utf-8'))
        elif isinstance(data, bytes):
            buf.write(f"${len(data)}\r\n".encode('utf-8'))
            buf.write(data)
            buf.write(b"\r\n")
        elif isinstance(data, int):
            buf.write(f":{data}\r\n".encode('utf-8'))
        elif isinstance(data, bool):
            buf.write(b"#t\r\n" if data else b"#f\r\n")
        elif isinstance(data, Error):
            buf.write(f"-{data.message}\r\n".encode('utf-8'))
        elif isinstance(data, (list, tuple)):
            buf.write(f"*{len(data)}\r\n".encode('utf-8'))
            for item in data:
                self._write(buf, item)
        elif isinstance(data, dict):
            buf.write(f"%{len(data)}\r\n".encode('utf-8'))
            for key, value in data.items():
                self._write(buf, key)
                self._write(buf, value)
        elif data is None:
            buf.write(b"$-1\r\n")
        else:
            raise CommandError(f"Unknown type: {type(data)}")
