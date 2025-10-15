import socket
from Errors import Error
from protocolHandler import ProtocolHandler
import time

class Client:
    def __init__(self, host='127.0.0.1', port=6666):
        self._protocol = ProtocolHandler()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._fh = self._socket.makefile('rwb')

    def execute(self, *args):
        start = time.time()
        try:
            self._protocol.write_response(self._fh, args)
            response = self._protocol.handle_request(self._fh)
        except (ConnectionResetError, BrokenPipeError):
            raise Exception("Connection to server lost")
        end = time.time()
        latency_ms = (end - start) * 1000
        if isinstance(response, Error):
            raise Exception(f"Error {response.code}: {response.message}")
        return response , latency_ms

    def get(self, key):
        return self.execute('GET', key)

    def set(self, key, value):
        return self.execute('SET', key, value)

    def delete(self, key):
        return self.execute('DELETE', key)

    def flush(self):
        return self.execute('FLUSH')

    def mget(self, *keys):
        return self.execute('MGET', *keys)

    def mset(self, *key_values):
        return self.execute('MSET', *key_values)

    def ping(self):
        return self.execute('PING')

    def close(self):
        try:
            self._fh.close()
        except Exception:
            pass
        self._socket.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def run():
    """Interactive command-line client for KrishnaDB"""
    print("⚡ KrishnaDB Client — type commands like Redis (e.g. SET key value, GET key)")
    print("Type 'exit' or 'quit' to close.\n")

    try:
        client = Client()
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return

    while True:
        try:
            cmd = input("krishnadb> ").strip()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit"):
                print("👋 Goodbye!")
                client.close()
                break

            parts = cmd.split()
            response,latency = client.execute(*parts)
            print(f"-> {response} (Latency: {latency:.2f}ms)")

        except KeyboardInterrupt:
            print("\n👋 Exiting KrishnaDB client.")
            client.close()
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    run()
