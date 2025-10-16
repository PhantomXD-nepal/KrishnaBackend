# client.py
import socket
from protocolHandler import ProtocolHandler
import time

class Client:
    def __init__(self, host='127.0.0.1', port=6666):
        self._protocol = ProtocolHandler()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._fh = self._socket.makefile('rwb')

    def execute(self, *args):
        start = time.perf_counter()
        self._protocol.write_response(self._fh, args)
        response = self._protocol.handle_request(self._fh)
        end = time.perf_counter()
        latency_ms = (end - start) * 1000
        return response, latency_ms

    def get(self, key):
        return self.execute('GET', key)

    def testinsert(self,key,size_kb):
        return self.execute('TESTINSERT',key,str(size_kb))

    def set(self, key, value):
        return self.execute('SET', key, value)

    def setfile(self, key, filepath):
        return self.execute('SETFILE', key, filepath)

    def getsize(self, key):
        return self.execute('GETSIZE', key)

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
        except:
            pass
        self._socket.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def run():
    print("⚡ KrishnaDB Client — supports SETFILE and GETSIZE")
    client = Client()
    while True:
        try:
            cmd = input("krishnadb> ").strip()
            if cmd.lower() in ("exit", "quit"):
                client.close()
                break
            if not cmd:
                continue
            parts = cmd.split()
            response, latency = client.execute(*parts)
            print(f"-> {response} (Latency: {latency:.3f} ms)")
        except KeyboardInterrupt:
            client.close()
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    run()
