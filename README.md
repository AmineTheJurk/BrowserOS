# BrowserOS

A free, retro CRT-styled Linux terminal that runs in the browser, deployable on [Render](https://render.com).

## What it is

- A green-phosphor, scanline terminal UI (HTML/CSS/JS + Socket.IO)
- A Python (Flask + Flask-SocketIO) backend
- Each visitor gets an isolated, temporary sandbox directory
- Commands are restricted to a safe allow-list (`ls`, `cat`, `python3`, `gcc`, etc.), with a timeout and output cap
- A tiny separate `redirect.py` Flask app to forward a custom domain to the live Render URL

## Why sandboxed, not a real root shell

A truly open, unauthenticated, free public shell is an easy target for abuse (crypto-mining, attack launching, etc.), and most hosts (including Render) will suspend an app like that. This keeps the "type real commands, get real output" feel while staying safe to leave public.

## Deploy on Render

1. Push this repo to GitHub (done: `AmineTheJurk/BrowserOS`)
2. On Render: New -> Web Service -> connect this repo
3. Render will detect `render.yaml` automatically (build: `pip install -r requirements.txt`, start: `gunicorn -k eventlet -w 1 app:app`)
4. Free plan works fine for this

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000`.

## Files

- `app.py` - backend + sandbox logic
- `templates/index.html` - retro terminal frontend
- `render.yaml` - Render deploy config
- `redirect.py` - standalone redirector to the live Render URL
- `sandbox/hello.c` - sample C file you can compile inside the sandbox with `gcc`
