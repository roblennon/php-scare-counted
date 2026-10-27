# Expected probe results (php 8.4.26, post_max_size=2M, ~3MB chunked body)

| front door | what happens | why |
|---|---|---|
| bare-apache (mod_php) `:8401` | `post_fields=1` — the body PARSED | mod_php reads the request body directly; no Content-Length exists to check, so `post_max_size` is never consulted. The parser streams unbounded. |
| nginx -> fpm `:8402` | rejected (413) | nginx buffers the entire body, counts it, enforces `client_max_body_size`/forwards a synthesized Content-Length. The limit comes back. |
| proxy_fcgi -> fpm `:8403` | `post_fields=0` — SKIPPED | FPM receives a multipart body with no Content-Length and declines to parse it at all. The safest failure available: refuse the work. |

Bare Apache is the exposed configuration; the other two are closed by
architecture (one by counting, one by refusing). LiteSpeed/lsapi is a dead
end for this shape (different body handling; bring your own instance).

The `php:8.4.26` images set no small post_max_size by default (128M/8M in
php.ini-production), so mount `php-overrides.ini` if your probe needs the
2M/3M sizing used here — or just send a body larger than your actual limits.
