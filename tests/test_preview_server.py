import unittest
import sys
import threading
import time
import urllib.request
from pathlib import Path

# Add repo root and tools directory to sys.path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

# Import the module
try:
    import preview_server
    from preview_server import HTTPServer
except ImportError as e:
    preview_server = None
    import_error = e

class TestPreviewServer(unittest.TestCase):
    def test_import_success(self):
        self.assertIsNotNone(preview_server, f"Failed to import preview_server: {import_error if 'import_error' in locals() else 'Unknown error'}")

    def test_server_lifecycle(self):
        self.assertIsNotNone(preview_server, "preview_server module not imported")
        
        # We start HTTPServer on port 0 to let OS assign a free ephemeral port
        # Using preview_server's PreviewHandler
        server = HTTPServer(("127.0.0.1", 0), preview_server.PreviewHandler)
        port = server.server_port
        self.assertGreater(port, 0, "Server failed to allocate a valid port")

        # Start serve_forever in a daemon thread so it doesn't hang the test suite
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        # Let the server initialize
        time.sleep(0.2)

        try:
            # Verify we can make a simple HTTP request to the root path
            # It should render the template gallery page
            url = f"http://127.0.0.1:{port}/"
            with urllib.request.urlopen(url, timeout=5) as response:
                self.assertEqual(response.status, 200)
                html = response.read().decode("utf-8")
                self.assertIn("GoPhish Template Gallery", html)
        finally:
            # Shut down cleanly
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

if __name__ == "__main__":
    unittest.main()
