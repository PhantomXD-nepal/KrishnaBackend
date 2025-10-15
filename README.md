# KrishnaDB Protocol Documentation

KrishnaDB is a lightweight key-value store with a custom protocol inspired by Redis. This document describes how clients and servers communicate using different data types.

---

## Protocol Overview

Each message sent to or received from the server begins with a **prefix character** that identifies the data type. The message is terminated by `\r\n`.

The supported data types and their formats are summarized below.

| Data Type         | Prefix | Structure                                           | Example |
|------------------|--------|----------------------------------------------------|----------|
| **Simple string** | `+`    | `+{string data}\r\n`                               | `+this is a simple string\r\n` |
| **Error**         | `-`    | `-{error message}\r\n`                             | `-ERR unknown command "FLUHS"\r\n` |
| **Integer**       | `:`    | `:{number}\r\n`                                    | `:1337\r\n` |
| **Binary / Bulk string** | `$` | `${number of bytes}\r\n{data}\r\n`              | `$6\r\nfoobar\r\n` |
| **Array**         | `*`    | `*{number of elements}\r\n{elements}\r\n`         | `*3\r\n+a simple string element\r\n:12345\r\n$7\r\ntesting\r\n` |
| **Dictionary**    | `%`    | `%{number of keys}\r\n{key/value pairs}\r\n`      | `%3\r\n+key1\r\n+value1\r\n+key2\r\n*2\r\n+value2-0\r\n+value2-1\r\n:3\r\n$7\r\ntesting\r\n` |
| **NULL**          | `$`    | `$-1\r\n` (represents null string)                 | `$-1\r\n` |

---

## Details

### 1. Simple String (`+`)
- Used to send plain text messages.
- Does not support newlines in the message.
- **Example:**
```text
+OK\r\n

2. Error (-)

Indicates a command or protocol error.

Clients should handle errors appropriately.

Example:

-ERR unknown command "FLUHS"\r\n

3. Integer (:)

Represents numeric values.

Example:

:1337\r\n

4. Binary / Bulk String ($)

Used for strings that may contain spaces or special characters.

Includes the length of the string in bytes.

Example:

$6\r\nfoobar\r\n

5. Array (*)

Represents a list of elements.

Elements can be any of the supported data types (strings, integers, arrays, etc.).

Example:

*3\r\n+a simple string element\r\n:12345\r\n$7\r\ntesting\r\n

6. Dictionary (%)

Represents key-value pairs.

Keys and values can be any supported data type.

Example:

%3\r\n+key1\r\n+value1\r\n+key2\r\n*2\r\n+value2-0\r\n+value2-1\r\n:3\r\n$7\r\ntesting\r\n

7. NULL ($-1)

Represents a null value.

Can be used for strings, arrays, or dictionaries.

Example:

$-1\r\n

Notes

All numeric lengths and counts are expressed as decimal numbers.

Arrays and dictionaries are recursive, so elements may contain other arrays or dictionaries.

Clients must always read the prefix byte first to determine the data type.

Quick Start Example

Here is how a client can send SET and GET commands using the KrishnaDB protocol.

Example: SET a key
Command:
*3\r\n$3\r\nSET\r\n$8\r\nuser:123\r\n$23\r\n{"name":"Alice","age":25}\r\n

Server Response:
+OK\r\n

Example: GET a key
Command:
*2\r\n$3\r\nGET\r\n$8\r\nuser:123\r\n

Server Response:
$23\r\n{"name":"Alice","age":25}\r\n

Notes:

Arrays (*) are used for commands with multiple arguments.

Strings ($) indicate the length and the content.

Responses follow the same prefix-based structure:

+ for success messages

$ for bulk string data

- for errors
