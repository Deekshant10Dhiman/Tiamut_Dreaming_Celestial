"""Tiamut validator for Vercel (Python runtime, stdlib only).
GET  /                 -> form
GET  /?tag=6571e95b    -> check
POST /  (tag=...)      -> check (form or JSON {"tag": "..."})
"""
import json, hmac, re
from html import escape
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

TAG  = "6571e95b"                                   # trace-tag of the AWAKE run
FLAG = "GDG{tiamut_is_awake_now_you_face_arishem}"

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Tiamut</title>
<style>body{{background:#0b0a12;color:#e8e4f0;font:16px/1.5 system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;margin:0}}
main{{width:min(92vw,460px)}}h1{{font-weight:600;letter-spacing:.04em}}p{{color:#a9a3bd}}
input,button{{font:inherit;padding:.7em 1em;border-radius:8px;border:1px solid #3a3555;background:#15132280;color:inherit;width:100%;box-sizing:border-box}}
button{{margin-top:.6em;background:#7c5cff;border:0;cursor:pointer;font-weight:600}}
.r{{margin-top:1.2em;padding:1em;border-radius:8px;background:#15132a;word-break:break-all}}.ok{{border-left:4px solid #4ade80}}.no{{border-left:4px solid #f87171}}</style>
<main><h1>Tiamut, the Dreaming Celestial</h1>
<p>Submit the trace-tag printed when the dream ends in AWAKE.</p>
<form method=post><input name=tag placeholder="trace-tag (8 hex digits)" autocomplete=off autofocus>
<button>Speak</button></form>{result}</main>"""

def check(raw):
    t = re.sub(r"^0x", "", (raw or "").strip().lower())
    ok = hmac.compare_digest(t.encode(), TAG.encode())
    return ok, ({"result": "AWAKE", "flag": FLAG} if ok else {"result": "DORMANT"})

class handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        b = body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(b)

    def _answer(self, tag, wants_json):
        if tag is None:
            return self._send(200, PAGE.format(result=""), "text/html; charset=utf-8")
        ok, obj = check(tag)
        if wants_json:
            return self._send(200 if ok else 403, json.dumps(obj), "application/json")
        msg = ("The Celestial wakes. <b>%s</b>" % escape(FLAG)) if ok else "Tiamut sleeps on. Wrong tag."
        r = '<div class="r %s">%s</div>' % ("ok" if ok else "no", msg)
        self._send(200, PAGE.format(result=r), "text/html; charset=utf-8")

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        tag = q.get("tag", [None])[0]
        self._answer(tag, "json" in q)

    def do_POST(self):
        n = min(int(self.headers.get("Content-Length") or 0), 4096)
        body = self.rfile.read(n).decode("utf-8", "ignore")
        if "json" in (self.headers.get("Content-Type") or ""):
            try: tag = str(json.loads(body).get("tag", ""))
            except Exception: tag = ""
            return self._answer(tag, True)
        self._answer(parse_qs(body).get("tag", [""])[0], False)

    def log_message(self, *a): pass
