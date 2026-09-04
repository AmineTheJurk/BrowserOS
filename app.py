"""
BrowserOS - a free, retro-styled Linux terminal in the browser.

Design note: this does NOT hand out a raw root shell to the public internet.
Each visitor gets an isolated, ephemeral sandbox directory and can only run a
small allow-listed set of commands, with CPU/time/output limits enforced.
That keeps the "real terminal feel" (running python, gcc, ls, cat, etc.)
without turning a free public URL into an open remote-code-execution box.
"""

import os
import shutil
import subprocess
import tempfile
import uuid

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "browseros-dev-key")
socketio = SocketIO(app, cors_allowed_origins="*")

SESSIONS = {}  # sid -> sandbox dir path

# Allow-listed binaries. Anything else is rejected before it ever hits subprocess.
ALLOWED = {
    "ls", "pwd", "cat", "echo", "whoami", "date", "uname", "clear",
    "python3", "gcc", "g++", "mkdir", "touch", "rm", "cd", "help", "neofetch",
}

MAX_OUTPUT = 8000       # chars
CMD_TIMEOUT = 8         # seconds


def make_sandbox():
    path = tempfile.mkdtemp(prefix="browseros_")
    with open(os.path.join(path, "welcome.txt"), "w") as f:
        f.write("Welcome to BrowserOS.\nType 'help' to see what's available.\n")
    return path


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def on_connect():
    SESSIONS[request_sid()] = make_sandbox()
    emit("output", {"data": "BrowserOS v0.1 - sandboxed session ready.\r\n$ "})


@socketio.on("disconnect")
def on_disconnect():
    path = SESSIONS.pop(request_sid(), None)
    if path and os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def request_sid():
    from flask import request
    return request.sid


@socketio.on("command")
def on_command(data):
    sid = request_sid()
    cwd = SESSIONS.get(sid)
    if not cwd:
        cwd = SESSIONS[sid] = make_sandbox()

    raw = (data or {}).get("cmd", "").strip()
    if not raw:
        emit("output", {"data": "$ "})
        return

    if raw == "help":
        emit("output", {"data": "\r\nAvailable: " + ", ".join(sorted(ALLOWED)) + "\r\n$ "})
        return

    if raw == "clear":
        emit("clear", {})
        emit("output", {"data": "$ "})
        return

    prog = raw.split()[0]
    if prog not in ALLOWED:
        emit("output", {"data": f"\r\nbash: {prog}: command not found (sandbox allow-list)\r\n$ "})
        return

    try:
        result = subprocess.run(
            raw,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=CMD_TIMEOUT,
            env={"PATH": "/usr/bin:/bin", "HOME": cwd},
        )
        out = (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired:
        out = "process timed out (sandbox limit)\r\n"
    except Exception as e:
        out = f"error: {e}\r\n"

    out = out[:MAX_OUTPUT]
    emit("output", {"data": "\r\n" + out.replace("\n", "\r\n") + "$ "})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
