

# KrishnaDB Protocol Documentation

KrishnaDB is a lightweight key-value store with a **Redis-inspired binary-safe protocol**.
All data communication follows a simple rule:
Each value starts with a **prefix character** denoting its type, and ends with `\r\n`.

---

## 📘 Supported Data Types

| Data Type                    | Prefix | Structure                               | Example                                                 |                                       |
| ---------------------------- | ------ | --------------------------------------- | ------------------------------------------------------- | ------------------------------------- |
| **Simple String**            | `+`    | `+{string data}\r\n`                    | `+this is a simple string\r\n`                          |                                       |
| **Error**                    | `-`    | `-{error message}\r\n`                  | `-ERR unknown command "FLUHS"\r\n`                      |                                       |
| **Integer**                  | `:`    | `:{number}\r\n`                         | `:1337\r\n`                                             |                                       |
| **Binary / Bulk String**     | `$`    | `${length}\r\n{data}\r\n`               | `$6\r\nfoobar\r\n`                                      |                                       |
| **Array**                    | `*`    | `*{count}\r\n{elements}\r\n`            | `*3\r\n+a simple string\r\n:12345\r\n$7\r\ntesting\r\n` |                                       |
| **Dictionary (Hash/Object)** | `%`    | `%{key_count}\r\n{key/value pairs}\r\n` | `%2\r\n+name\r\n+KrishnaDB\r\n+version\r\n:1\r\n`       |                                       |
| **NULL**                     | `$`    | `$-1\r\n`                               | `$-1\r\n`                                               |                                       |
| **Boolean**                  | `#`    | `#{t`                                   | `f}`\r\n`                                                 | `#t\r\n` → `True`, `#f\r\n` → `False` |

---

## 🔢 Boolean Type

The **Boolean** data type (`#`) is used for representing `True` and `False` values.

| Value | Raw Protocol | Python Equivalent |
| ----- | ------------ | ----------------- |
| True  | `#t\r\n`     | `True`            |
| False | `#f\r\n`     | `False`           |

**Example Interaction:**

```
Client → $3\r\nSET\r\n+flag\r\n#t\r\n
Server → +OK (stored as bool)\r\n

Client → $3\r\nGET\r\n+flag\r\n
Server → #t\r\n
```

---

## ⚡ Performance Metrics and Testing

KrishnaDB supports **latency and throughput testing** directly from the client using built-in diagnostic commands.

### 🔹 `PING`

Measures **round-trip latency** between client and server.

```bash
krishnadb> PING
-> PONG (Latency: 0.32ms)
```

---

### 🔹 `TEST {size_in_kb}`

Generates and inserts random test data of the specified size to measure **insertion latency** and **storage throughput**.

#### Example:

```bash
krishnadb> TESTINSERT <testname> <size_in_kb>
-> OK - inserted 10 KB of random data (Latency: 4.7 ms)
```

#### Output metrics:

* **Insertion Latency:** Time taken to store the generated data.
* **Data Size:** Approximate payload in kilobytes.
* **Throughput:** Data written per second (calculated as size ÷ latency).

---

### 🔹 `METRICS`

Displays cumulative statistics of recent operations.

### 🧪 Example Testing Session

```bash
krishnadb> SET user {"name": "Krishna", "active": true, "role": "admin"}
-> OK (stored as dict) (Latency: 4.75ms)

krishnadb> GET user
-> dict: {'name': 'Krishna', 'active': True, 'role': 'admin'} (Latency: 0.31ms)

krishnadb> TEST test1 512
-> OK - inserted 512 KB of random data (Latency: 38.2ms)

```

---

Would you like me to generate the actual `TEST` and `METRICS` command implementation for your server next?
