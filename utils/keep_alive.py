import os
import time
import logging
from flask import Flask
from threading import Thread
import urllib.request

app = Flask(__name__)
log = logging.getLogger("keep_alive")

@app.route('/')
def home():
    return "Bot is alive and running 24/7! 🏏"

def run():
    port = int(os.environ.get("PORT", 8080))
    # Suppress Flask default logging
    import logging as flask_logging
    flask_log = flask_logging.getLogger('werkzeug')
    flask_log.setLevel(flask_logging.ERROR)
    
    app.run(host="0.0.0.0", port=port)

def ping():
    """Periodically ping the server to prevent it from sleeping."""
    port = int(os.environ.get("PORT", 8080))
    url = os.environ.get("PUBLIC_URL", f"http://127.0.0.1:{port}")
    
    while True:
        try:
            time.sleep(240)  # Ping every 4 minutes
            urllib.request.urlopen(url)
            log.debug(f"Self-pinged {url} to keep server alive.")
        except Exception as e:
            log.debug(f"Self-ping failed: {e}")

def keep_alive():
    """Starts the Flask server and the self-pinging thread."""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    p = Thread(target=ping)
    p.daemon = True
    p.start()
