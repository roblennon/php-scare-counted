#!/usr/bin/env python3
"""Benign self-check probe: one small multipart POST with an upload-progress
field to YOUR OWN check.php endpoint. Sized in kilobytes; no memory games.

Usage:  python3 probe.py https://your.site/path/to/check.php
"""
import json, sys, urllib.request, uuid

url = sys.argv[1] if len(sys.argv) > 1 else None
if not url:
    sys.exit("usage: probe.py https://your.site/path/to/check.php")

boundary = "----psc" + uuid.uuid4().hex
name = "psc" + uuid.uuid4().hex[:8]
body = (
    f"--{boundary}\r\n"
    f"Content-Disposition: form-data; name=\"PHPSESSID\"\r\n\r\n{name}\r\n"
    f"--{boundary}\r\n"
    f"Content-Disposition: form-data; name=\"PHP_SESSION_UPLOAD_PROGRESS\"\r\n\r\n{name}\r\n"
    f"--{boundary}\r\n"
    f"Content-Disposition: form-data; name=\"f\"; filename=\"t.txt\"\r\n"
    f"Content-Type: text/plain\r\n\r\nhello\r\n"
    f"--{boundary}--\r\n"
).encode()

req = urllib.request.Request(url, data=body, method="POST", headers={
    "Content-Type": f"multipart/form-data; boundary={boundary}",
    "Cookie": f"PHPSESSID={name}",
})
with urllib.request.urlopen(req, timeout=30) as r:
    out = json.load(r)

enabled = out.get("ini", {}).get("session.upload_progress.enabled")
print(json.dumps(out, indent=2))
print()
if enabled in ("1", "On", "on", True):
    print("MACHINERY ON  — the upload-progress engine engages on this host.")
    print("That is PHP's default. If you are on an end-of-life version you")
    print("cannot patch, PHP's own interim guidance (also for CVE-2026-115560)")
    print("is to set session.upload_progress.enabled=0 if you don't use it.")
else:
    print("MACHINERY OFF — every public chain for the 2026-10 PHP2Shell pair,")
    print("and PHP's own interim guidance for CVE-2026-115560, stops here.")
print("\nNow delete check.php from your server.")
