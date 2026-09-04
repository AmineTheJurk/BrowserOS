"""
Tiny standalone redirector.

Deploy this by itself (e.g. as a second, trivial Render/Flask service, or
behind a custom domain) to bounce visitors straight to the real BrowserOS
app running on Render. Set RENDER_URL to your actual deployed URL.
"""

import os
from flask import Flask, redirect

app = Flask(__name__)
RENDER_URL = os.environ.get("RENDER_URL", "https://browseros.onrender.com")


@app.route("/")
def go():
    return redirect(RENDER_URL, code=302)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
