import socket
import requests
import threading
import logging
import time
from contextlib import closing
from typing import Optional
from flask import Flask, render_template, request


def is_server_running(port: int) -> bool:
    """
    Check if a server is already running on the specified port.

    Args:
        port (int): Port number to check

    Returns:
        bool: True if server is running, False otherwise
    """
    try:
        # Try to connect to the server
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            result = sock.connect_ex(("localhost", port))
            if result == 0:
                # Port is open, try to make a request to verify it's our server
                try:
                    response = requests.get(
                        f"http://localhost:{port}/register_start", timeout=1
                    )
                    return "doomarena" in response.text.lower()
                except requests.RequestException:
                    return False
            return False
    except:
        return False


def spawn_server(server_port: int):
    """
    Spawn a Flask server if one isn't already running on the specified port.

    Args:
        server_port (int): Port to run the server on
    """
    # Check if server is already running
    if is_server_running(server_port):
        print(f"Server already running on port {server_port}")
        return

    def run_server():
        app = Flask(__name__)

        # Configure logging with a prefix
        logging.basicConfig(
            filename="server.log",  # Log file name
            level=logging.INFO,  # Logging level
            format="Malicious server - %(asctime)s - %(message)s",  # Prefix added to logs
        )

        @app.route("/", methods=["GET"])
        @app.route("/register_start", methods=["GET"])
        def register_start():
            query_params = request.args.to_dict()
            logging.info(f"Received GET request with query params: {query_params}")
            return render_template("pirate.html"), 200

        app.run(host="localhost", port=server_port, debug=False)

    # Start the server in a new thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait a bit to ensure server starts up
    time.sleep(1)

    # Verify server started successfully
    if is_server_running(server_port):
        print(f"Server successfully started on port {server_port}")
    else:
        print(f"Failed to start server on port {server_port}")
