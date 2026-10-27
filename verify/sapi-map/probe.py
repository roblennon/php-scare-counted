#!/usr/bin/env python3
"""Sends one chunked (Content-Length-less) multipart body, ~3MB, past a 2M
post_max_size, at each front door. What each door DOES with it is the map.
Reads the JSON from echo.php and classifies:
  parsed    -> body reached the parser uncounted (limit never consulted)
  rejected  -> the tier in front counted the bytes and said no
  skipped   -> the parser declined a CL-less multipart entirely
"""
import json, socket, sys

BOUNDARY = "----pscprobe"
TARGETS = [
    ("bare-apache (mod_php)", 8401, "parsed expected: chunked streams unbounded"),
    ("nginx -> fpm",          8402, "rejected expected: nginx buffers + counts, limit enforced"),
    ("proxy_fcgi -> fpm",     8403, "skipped expected: FPM declines CL-less multipart"),
]

def chunk(data: bytes) -> bytes:
        out = b""
        for i in range(0, len(data), 8192):
            c = data[i:i+8192]
            out += hex(len(c))[2:].encode() + b"\r\n" + c + b"\r\n"
        return out + b"0\r\n\r\n"

def probe(name: str, port: int, note: str) -> str:
    part = (f"--{BOUNDARY}\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n" + "A" * (3 * 1024 * 1024) + f"\r\n--{BOUNDARY}--\r\n").encode()
    headers = ("POST /echo.php HTTP/1.1\r\nHost: localhost\r\n"
               f"Content-Type: multipart/form-data; boundary={BOUNDARY}\r\n"
               "Transfer-Encoding: chunked\r\nConnection: close\r\n\r\n")
    req = headers.encode() + chunk(part)
    s = socket.create_connection(("127.0.0.1", port), timeout=30)
    s.sendall(req)
    buf = b""
    while True:
        d = s.recv(65536)
        if not d: break
        buf += d
    s.close()
    head, _, body = buf.partition(b"\r\n\r\n")
    status = head.split(b"\r\n")[0].decode(errors="replace")
    try:
        j = json.loads(body.strip().splitlines()[-1])
    except Exception:
        return f"{name:24} {status}  [no JSON]  <- {note}"
    return f"{name:24} {status}  post_fields={j['post_fields']} files={j['files']} cl={j['content_length_seen']}  <- {note}"

if __name__ == "__main__":
    for name, port, note in TARGETS:
        try:
            print(probe(name, port, note))
        except Exception as e:
            print(f"{name:24} unreachable ({e}) — is the compose stack up?")
    sys.exit(0)
