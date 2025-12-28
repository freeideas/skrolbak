#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Simple HTTP server for testing web applications.

Starts an HTTP server on a randomly chosen available port above 10000.
Can be used as a module or run directly.

Module usage:
    from websrvr import start_server, stop_server

    port = start_server('./released')
    # ... run tests against http://localhost:{port} ...
    stop_server()

Command-line usage:
    websrvr.py <directory>
    # Prints port number and runs until Ctrl+C
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import atexit
import http.server
import random
import socket
import socketserver
import threading
import time
from pathlib import Path

# Global server reference for cleanup
_server = None
_server_thread = None


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that suppresses request logging."""

    def __init__(self, *args, directory=None, **kwargs):
        self._directory = directory
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        """Suppress all log messages."""
        pass


def find_available_port(min_port=10000, max_port=60000):
    """
    Find an available port by trying random ports above min_port.

    Args:
        min_port: Minimum port number (default: 10000)
        max_port: Maximum port number (default: 60000)

    Returns:
        int: An available port number

    Raises:
        RuntimeError: If no available port found after many attempts
    """
    for _ in range(100):
        port = random.randint(min_port, max_port)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find available port between {min_port} and {max_port}")


def start_server(directory, port=None):
    """
    Start an HTTP server serving files from the specified directory.

    Args:
        directory: Path to the directory to serve (str or Path)
        port: Optional specific port to use. If None, finds an available port.

    Returns:
        int: The port number the server is listening on

    Raises:
        FileNotFoundError: If the directory doesn't exist
        RuntimeError: If server fails to start
    """
    global _server, _server_thread

    # Validate directory
    dir_path = Path(directory).resolve()
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {dir_path}")
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")

    # Stop any existing server
    stop_server()

    # Find port if not specified
    if port is None:
        port = find_available_port()

    # Create handler class with directory bound
    def handler_factory(*args, **kwargs):
        return QuietHTTPRequestHandler(*args, directory=str(dir_path), **kwargs)

    # Allow port reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True

    try:
        _server = socketserver.TCPServer(("0.0.0.0", port), handler_factory)
    except OSError as e:
        raise RuntimeError(f"Failed to start server on port {port}: {e}")

    # Run server in a daemon thread
    _server_thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _server_thread.start()

    # Wait briefly and verify server is running
    time.sleep(0.1)
    if not _server_thread.is_alive():
        raise RuntimeError("Server thread died unexpectedly")

    return port


def stop_server():
    """
    Stop the running HTTP server if one exists.

    Safe to call multiple times or when no server is running.
    """
    global _server, _server_thread

    if _server is not None:
        try:
            _server.shutdown()
            _server.server_close()
        except Exception:
            pass
        _server = None

    if _server_thread is not None:
        try:
            _server_thread.join(timeout=2)
        except Exception:
            pass
        _server_thread = None


def get_server_url(port):
    """
    Get the full URL for accessing the server.

    Args:
        port: The port number

    Returns:
        str: URL like "http://localhost:12345"
    """
    return f"http://localhost:{port}"


# Register cleanup on exit
atexit.register(stop_server)


def main():
    """Command-line interface: serve a directory and print the port."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Start an HTTP server for testing web applications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./released
  %(prog)s ./released --port 8080

The server runs until interrupted with Ctrl+C.
        """
    )
    parser.add_argument(
        'directory',
        help='Directory to serve'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=None,
        help='Specific port to use (default: random available port above 10000)'
    )

    args = parser.parse_args()

    try:
        port = start_server(args.directory, args.port)
        url = get_server_url(port)
        print(f"Serving {args.directory} at {url}")
        print(f"Port: {port}")
        print("Press Ctrl+C to stop...")

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        stop_server()
        sys.exit(0)


if __name__ == '__main__':
    main()
