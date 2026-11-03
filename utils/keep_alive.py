"""
KhelBot Keep-Alive & Health Check Server.
Exposes / and /health HTTP routes to fulfill cloud container health checks (e.g. Railway, Render).
"""

import os
import time
import logging
from threading import Thread
import urllib.request
from flask import Flask, jsonify

app = Flask(__name__)
log = logging.getLogger("keep_alive")


@app.route("/")
def home():
    return "🏏 KhelBot V4 is alive and running 24/7!"


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "khelbot",
        "timestamp": time.time()
    }), 200


def run():
    port = int(os.environ.get("PORT", 8080))
    import logging as flask_logging
    flask_log = flask_logging.getLogger("werkzeug")
    flask_log.setLevel(flask_logging.ERROR)
    
    try:
        app.run(host="0.0.0.0", port=port, use_reloader=False)
    except Exception as e:
        log.warning(f"Keep-alive webserver stopped: {e}")


def ping():
    """Periodically ping the health endpoint to prevent sleep."""
    port = int(os.environ.get("PORT", 8080))
    url = os.environ.get("PUBLIC_URL", f"http://127.0.0.1:{port}/health")
    
    while True:
        try:
            time.sleep(240)  # Every 4 minutes
            req = urllib.request.Request(url, headers={"User-Agent": "KhelBot-SelfPing/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                pass
            log.debug("Self-ping successful")
        except Exception as e:
            log.debug(f"Self-ping notice: {e}")


def keep_alive():
    """Starts the Flask server and the self-pinging thread."""
    t = Thread(target=run, name="khelbot_keepalive_http")
    t.daemon = True
    t.start()
    
    p = Thread(target=ping, name="khelbot_self_ping")
    p.daemon = True
    p.start()
