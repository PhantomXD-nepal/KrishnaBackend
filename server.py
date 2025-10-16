# server.py
import time
import json
from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer
from Errors import CommandError, DisconnectError, Error
from protocolHandler import ProtocolHandler
from storage import Storage
import atexit
import os
import random

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
                    break
                if not data:
                    continue
                try:
                    response = self.get_response(data)
                except CommandError as exc:
                    response = Error(exc.args[0], code=500)
                start = time.perf_counter()
                self._protocol_handler.write_response(socket_file, response)
                end = time.perf_counter()
                print(f"🕒 Response latency: {(end-start)*1000:.3f} ms")
        finally:
            socket_file.close()
            conn.close()

    def get_commands(self):
        return {
            'PING': self.ping,
            'GET': self.get,
            'SET': self.set,
            'DELETE': self.delete,
            'FLUSH': self.flush,
            'MGET': self.mget,
            'MSET': self.mset,
            'EDIT': self.edit,
            'SETFILE': self.setfile,
            'GETSIZE': self.getsize,
            'TESTINSERT':self.testinsert
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

    def ping(self):
        return "PONG"

    def testinsert(self,key, size_kb):
        start = time.perf_counter()
        try:
            size_kb = int(size_kb)
        except ValueError:
            return "Size must be an integer (KB)"
        total_bytes = size_kb * 1024
        payload = [random.randint(0, 9999) for _ in range(total_bytes // 4)]  # 4 bytes per int approx
        self._kv[key] = payload
        end = time.perf_counter()
        latency_us = (end - start) * 1_000_000
        actual_size = len(payload) * 4
        return f"OK - inserted test payload '{key}' ({actual_size} bytes, latency {latency_us:.2f} µs)"

    def get(self, key):
        value = self._kv.get(key)
        if value is None:
            return "(nil)"
        size = len(json.dumps(value).encode('utf-8')) if not isinstance(value, bytes) else len(value)
        return f"{type(value).__name__}: {value} (Size: {size} bytes)"

    def set(self, key, *value_parts):
        start = time.perf_counter()
        value_str = " ".join(value_parts).strip()
        value = None
        if (value_str.startswith("{") and value_str.endswith("}")) or (value_str.startswith("[") and value_str.endswith("]")):
            try:
                value = json.loads(value_str)
            except:
                value = value_str
        else:
            lower_val = value_str.lower()
            if lower_val == "true":
                value = True
            elif lower_val == "false":
                value = False
            elif value_str.isdigit():
                value = int(value_str)
            else:
                try:
                    value = float(value_str)
                except:
                    value = value_str
        self._kv[key] = value
        end = time.perf_counter()
        size = len(json.dumps(value).encode('utf-8')) if not isinstance(value, bytes) else len(value)
        latency_us = (end - start) * 1_000_000
        print(f"🕒 Insertion latency: {latency_us:.2f} µs | Size: {size} bytes")
        return f"OK (stored as {type(value).__name__}, size: {size} bytes)"

    def setfile(self, key, filepath):
        start = time.perf_counter()
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        with open(filepath, "rb") as f:
            content = f.read()
        self._kv[key] = content
        end = time.perf_counter()
        size = len(content)
        latency_us = (end - start) * 1_000_000
        print(f"🕒 File insertion latency: {latency_us:.2f} µs | Size: {size} bytes")
        return f"OK (stored as bytes, size: {size} bytes)"

    def getsize(self, key):
        value = self._kv.get(key)
        if value is None:
            return "(nil)"
        size = len(json.dumps(value).encode('utf-8')) if not isinstance(value, bytes) else len(value)
        return f"Key '{key}' size: {size} bytes"

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
        return [f"{type(v).__name__}: {v}" if v is not None else "(nil)" for v in [self._kv.get(k) for k in keys]]

    def mset(self, *items):
        data = list(zip(items[::2], items[1::2]))
        for key, value in data:
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
