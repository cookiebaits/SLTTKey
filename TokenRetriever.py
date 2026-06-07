import hashlib
import json
import os
import base64
import socket
import threading
import webbrowser
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import requests

logger = logging.getLogger(__name__)

class TokenRetriever:
    """
    Handles the retrieval of Streamlabs OAuth tokens using PKCE (Proof Key for Code Exchange).
    """
    STREAMLABS_API_URL = "https://streamlabs.com/api/v5/slobs/auth/data"

    def __init__(self):
        """
        Initializes the TokenRetriever with a new code verifier and challenge.
        """
        self.code_verifier = self._generate_code_verifier()
        self.code_challenge = self._generate_code_challenge(self.code_verifier)
        self._auth_code: str | None = None
        self._server_event = threading.Event()

    # ------------------------------------------------------------------ #
    #  PKCE helpers                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _generate_code_verifier() -> str:
        """
        Generates a random 64-byte hex string to be used as the PKCE verifier.

        Returns:
            str: A 128-character hex string.
        """
        return os.urandom(64).hex()

    @staticmethod
    def _generate_code_challenge(verifier: str) -> str:
        """
        Generates a PKCE code challenge from the given verifier.

        Args:
            verifier (str): The PKCE verifier string.

        Returns:
            str: The base64url-encoded SHA-256 hash of the verifier.
        """
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    # ------------------------------------------------------------------ #
    #  Port helper                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_free_port() -> int:
        """
        Finds a free ephemeral port by binding to port 0.

        Returns:
            int: A free port number.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    # ------------------------------------------------------------------ #
    #  Local callback server                                               #
    # ------------------------------------------------------------------ #

    def _make_handler(self):
        """Return an HTTPServer request handler that captures the auth code."""
        retriever = self  # close over self

        class _CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)

                if params.get("success", [""])[0] == "true" and "code" in params:
                    retriever._auth_code = params["code"][0]
                    body = b"<h2>Authentication successful! You can close this tab.</h2>"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    body = b"<h2>Authentication failed. Please try again.</h2>"
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

                # signal the main thread regardless of outcome
                retriever._server_event.set()

            def log_message(self, *_):
                pass  # suppress default access log noise

        return _CallbackHandler

    def _start_callback_server(self, port: int) -> HTTPServer:
        """
        Starts a local HTTP server to listen for the OAuth callback.

        Args:
            port (int): The port to listen on.

        Returns:
            HTTPServer: The started HTTP server instance.
        """
        server = HTTPServer(("127.0.0.1", port), self._make_handler())
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server

    # ------------------------------------------------------------------ #
    #  Main entry point                                                    #
    # ------------------------------------------------------------------ #

    def retrieve_token(self, timeout: int = 300) -> str | None:
        """
        Open the Streamlabs login page in the user's default browser, wait for
        the OAuth callback on a local server, then exchange the code for a token.

        Args:
            timeout (int): seconds to wait for the user to complete login (default 5 min)

        Returns:
            str | None: The oauth_token string on success, or None on failure.
        """
        port = self._find_free_port()

        auth_url = (
            f"https://streamlabs.com/slobs/login?"
            f"skip_splash=true&external=electron&tiktok&force_verify"
            f"&origin=slobs&port={port}"
            f"&code_challenge={self.code_challenge}&code_flow=true"
        )

        server = self._start_callback_server(port)

        logger.info(f"Opening browser for Streamlabs login (callback on port {port})…")
        webbrowser.open(auth_url)

        completed = self._server_event.wait(timeout=timeout)
        threading.Thread(target=server.shutdown, daemon=True).start()

        if not completed:
            logger.error("Timed out waiting for the user to complete login.")
            return None

        if not self._auth_code:
            logger.error("Callback received but no auth code was present.")
            return None

        return self._exchange_code_for_token(self._auth_code)

    # ------------------------------------------------------------------ #
    #  Token exchange                                                      #
    # ------------------------------------------------------------------ #

    def _exchange_code_for_token(self, code: str) -> str | None:
        """
        Exchanges the authorization code for an OAuth token.

        Args:
            code (str): The authorization code received from the callback.

        Returns:
            str | None: The OAuth token if successful, None otherwise.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "StreamlabsDesktop/1.20.4 Chrome/122.0.6261.156 "
                "Electron/29.3.1 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "en-US",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        }
        params = {
            "code_verifier": self.code_verifier,
            "code": code,
        }

        try:
            response = requests.get(
                self.STREAMLABS_API_URL,
                params=params,
                headers=headers,
                timeout=30,
            )
        except requests.RequestException as e:
            logger.error(f"Network error during token exchange: {e}")
            return None

        if response.status_code != 200:
            logger.error(f"Token exchange failed: HTTP {response.status_code} — {response.text}")
            return None

        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error("Token exchange returned non-JSON response.")
            return None

        if not data.get("success"):
            logger.error(f"Streamlabs reported failure: {data}")
            return None

        token = data["data"].get("oauth_token")
        logger.info("Successfully obtained Streamlabs OAuth token.")
        return token