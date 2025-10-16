from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer
from Errors import CommandError, DisconnectError, Error
from protocolHandler import ProtocolHandler
from storage import Storage
import atexit
import json

class Server:
    def __init__(self, host='127.0.0.1', port=6666, max_clients=64):
        self._pool = Pool(max_clients)
        self._server = StreamServer((host, port), self.conn_handler, spawn=self._pool)
        self._protocol_handler = ProtocolHandler()
        self._storage_handler = Storage()
        self._kv = self._storage_handler.load_data()

        atexit.register(self._storage_handler.save_data, self._kv)

    def conn_handler(self, conn, addr):
        socket_file = conn.makefile('rwb')
        print(f"📡 Received connection from {addr}")
        try:
            while True:
                try:
                    data = self._protocol_handler.handle_request(socket_file)
                except DisconnectError:
                    print("❌ Client disconnected")
                    break

                if not data:
                    continue

                print("📩 Received data:", data)

                try:
                    response = self.get_response(data)
                except CommandError as exc:
                    response = Error(exc.args[0], code=500)

                # ✅ Send the response back to the client
                self._protocol_handler.write_response(socket_file, response)

        except Exception as e:
            print("⚠️ Error handling connection:", e)
        finally:
            socket_file.close()
            conn.close()
            print("🔌 Connection closed")

    def get_commands(self):
        return {
            'PING': self.ping,
            'GET': self.get,
            'SET': self.set,
            'DELETE': self.delete,
            'FLUSH': self.flush,
            'MGET': self.mget,
            'MSET': self.mset,
            'EDIT': self.edit
        }

    def get_response(self, request):
        if not isinstance(request, list):
            raise CommandError("Invalid command format")

        if not request:
            raise CommandError("Empty command")

        command = request[0].upper()
        commands = self.get_commands()

        if command not in commands:
            raise CommandError(f"Unknown command {command}")

        return commands[command](*request[1:])

    # ----- Commands -----
    def ping(self):
        return "PONG"

    def get(self, key):
        """Return both type and value."""
        value = self._kv.get(key)
        if value is None:
            return f"(nil)"
        return f"{type(value).__name__}: {value}"

    def set(self, key, *value_parts):
        value_str = " ".join(value_parts)

        # 🔍 Type detection
        if value_str.lower() in ["true", "false"]:
            value = value_str.lower() == "true"
        elif value_str.isdigit():
            value = int(value_str)
        else:
            try:
                value = float(value_str)
            except ValueError:
                value = value_str

        if (value_str.startswith("{") and value_str.endswith("}")) or (value_str.startswith("[") and value_str.endswith("]")):
            try:
                value = json.loads(value_str)
            except json.JSONDecodeError:
                value = value_str  # fallback if invalid JSON

        self._kv[key] = value
        return f"OK (stored as {type(value).__name__})"

    def delete(self, key):
        if key in self._kv:
            del self._kv[key]
            return "OK"
        return "Key not found"

    def flush(self):
        kvlen = len(self._kv)
        self._kv.clear()
        return f"OK - deleted {kvlen} keys"

    def mget(self, *keys):
        """Return list of (type: value) pairs."""
        return [f"{type(v).__name__}: {v}" if v is not None else "(nil)" for v in [self._kv.get(k) for k in keys]]

    def mset(self, *items):
        data = list(zip(items[::2], items[1::2]))
        for key, value in data:
            # store as string since MSET uses raw arguments
            self._kv[key] = value
        return f"OK {len(data)} items set"

    def edit(self, key, *value_parts):
        if key not in self._kv:
            return f"Key '{key}' not found."
        value_str = " ".join(value_parts)
        old_value = self._kv[key]
        new_value = value_str
        self._kv[key] = new_value
        return f"OK - updated '{key}' ({type(old_value).__name__}→{type(new_value).__name__})"

    def run(self):
        print("🚀 KrishnaDB Server started on 127.0.0.1:6666")
        self._server.serve_forever()


if __name__ == "__main__":
    Server().run()
