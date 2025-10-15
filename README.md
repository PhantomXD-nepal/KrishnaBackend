**Protocol Documentation**

| Data-type     | Prefix | Structure                                           | Example |
|----------------|--------|----------------------------------------------------|----------|
| **Simple string** | `+` | `+{string data}\r\n` | ```+this is a simple string\r\n``` |
| **Error** | `-` | `-{error message}\r\n` | ```-ERR unknown command "FLUHS"\r\n``` |
| **Integer** | `:` | `:{the number}\r\n` | ```:1337\r\n``` |
| **Binary** | `$` | `${number of bytes}\r\n{data}\r\n` | ```$6\r\nfoobar\r\n``` |
| **Array** | `*` | `*{number of elements}\r\n{0 or more of above}\r\n` | ```*3\r\n+a simple string element\r\n:12345\r\n$7\r\ntesting\r\n``` |
| **Dictionary** | `%` | `%{number of keys}\r\n{0 or more of above}\r\n` | ```%3\r\n+key1\r\n+value1\r\n+key2\r\n*2\r\n+value2-0\r\n+value2-1\r\n:3\r\n$7\r\ntesting\r\n``` |
| **NULL** | `$` | `$-1\r\n` (string of length -1) | ```$-1\r\n``` |
