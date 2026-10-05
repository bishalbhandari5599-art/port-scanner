Python Network Port Scanner
A beginner-friendly command-line program that checks whether TCP ports on one host accept connections. It uses only Python's standard library.
Use responsibly: Scan only computers and networks you own or have explicit permission to test. Port scans against other systems may be unauthorized or disruptive.
Requirements
    • Python 3.8 or newer
    • No third-party packages
Run it
From this folder, try a scan of your own computer:
python port_scanner.py 127.0.0.1
That checks ports 1 through 1024. Choose a smaller range to make a quick test:
python port_scanner.py 127.0.0.1 --start-port 1 --end-port 100
You can also set the connection timeout and number of concurrent checks:
python port_scanner.py 192.168.1.20 --start-port 8000 --end-port 8100 --timeout 1 --workers 20
Replace 192.168.1.20 with a device on your own network that you are authorized to test. Use python or python3 depending on your system.
Options
Option	Default	Meaning
target	—	Hostname or IPv4 address to check
--start-port	1	First TCP port in the range
--end-port	1024	Last TCP port in the range (included)
--timeout	0.5	Seconds to wait for each connection
--workers	100	Concurrent checks (allowed range: 1–500)

Run the tests
python -m unittest -v
The test opens a temporary TCP listener on the loopback interface (127.0.0.1) and checks that the scanner can detect it.
How it works
    1. Python resolves the target hostname to an IPv4 address.
    2. The scanner attempts a TCP connection to each port in the selected range.
    3. A successful connection is reported as open; unsuccessful or timed-out attempts are not reported as open.
    4. A small thread pool checks multiple ports concurrently.
This is a basic TCP checker, not a vulnerability scanner. It does not scan UDP, identify services, or bypass firewalls. A port not reported as open may be closed, filtered, or unreachable.
