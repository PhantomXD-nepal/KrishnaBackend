from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer
from Errors import CommandError, DisconnectError, Error
from protocolHandler import ProtocolHandler
import time
from storage import Storage
import atexit

class Server:
    def __init__(self, host='127.0.0.1', port=6666, max_clients=64):
        self._pool = Pool(max_clients)
        self._server = StreamServer(
            (host, port),
            self.conn_handler,
            spawn=self._pool
        )
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
            'EDIT':self.edit
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
        start = time.time()
        end = time.time()
        latency_ms = (end - start) * 1000
        return f"PONG latency: {latency_ms:.2f} ms"


    def get(self, key):
        return self._kv.get(key)

    def set(self, key, *value_parts):
        value = " ".join(value_parts)
        self._kv[key] = value
        return "OK"

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
        return [self._kv.get(key) for key in keys]

    def mset(self, *items):
        data = list(zip(items[::2], items[1::2]))
        for key, value in data:
            self._kv[key] = value
        return f"OK {len(data)} items set"

    def edit(self,key,*value_parts):
        if key not in self._kv:
            return f"Key '{key}' not found."
        if key in self._kv:
            value = " ".join(value_parts)
            old_value = self._kv[key]
            self._kv[key] = value
            return f"OK - updated key '{key}' (old value: '{old_value}', new value: '{value}')"
        else:
            return f"Key '{key}' not found."

    def run(self):
        print("🚀 KrishnaDB Server started on 127.0.0.1:6666")
        self._server.serve_forever()




if __name__ == "__main__":
    Server().run()
