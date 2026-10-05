import socket
import unittest

from port_scanner import scan_port, validate_options


class PortScannerTests(unittest.TestCase):
    def test_detects_open_local_port(self):
        # Bind only to loopback so this test never exposes a service to a network.
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]

        try:
            self.assertTrue(scan_port("127.0.0.1", port, timeout=0.5))
        finally:
            listener.close()

    def test_rejects_invalid_port_range(self):
        with self.assertRaises(ValueError):
            validate_options(0, 100, 0.5, 10)

        with self.assertRaises(ValueError):
            validate_options(200, 100, 0.5, 10)

    def test_rejects_nonpositive_timeout(self):
        with self.assertRaises(ValueError):
            validate_options(1, 100, 0, 10)


if __name__ == "__main__":
    unittest.main()
