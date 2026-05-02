from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running 24/7! 🏏"

def run():
    # Bind to 0.0.0.0 and port 8080 (or any PORT environment variable)
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    """Starts the Flask server in a separate thread to keep the bot alive."""
    t = Thread(target=run)
    t.daemon = True
    t.start()
