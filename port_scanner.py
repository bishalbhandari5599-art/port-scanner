#!/usr/bin/env python3
"""A small TCP port scanner for systems you own or are authorized to test."""

import argparse
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Sequence


def validate_options(start_port: int, end_port: int, timeout: float, workers: int) -> None:
    """Raise ValueError if a scan option is outside its safe/usable range."""
    if not 1 <= start_port <= 65535:
        raise ValueError("start port must be between 1 and 65535")
    if not 1 <= end_port <= 65535:
        raise ValueError("end port must be between 1 and 65535")
    if start_port > end_port:
        raise ValueError("start port cannot be greater than end port")
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0 seconds")
    if not 1 <= workers <= 500:
        raise ValueError("workers must be between 1 and 500")


def scan_port(host: str, port: int, timeout: float) -> bool:
    """Try one TCP connection; return True if the port accepts it."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            return client.connect_ex((host, port)) == 0
    except OSError:
        # A refused connection, timeout, or other socket error is not open.
        return False


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check a range of TCP ports on one host you are authorized to test."
    )
    parser.add_argument("target", help="hostname or IPv4 address to scan")
    parser.add_argument(
        "--start-port", type=int, default=1, help="first port to check (default: 1)"
    )
    parser.add_argument(
        "--end-port", type=int, default=1024, help="last port to check (default: 1024)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.5,
        help="seconds to wait for each connection (default: 0.5)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=100,
        help="number of concurrent checks, from 1 to 500 (default: 100)",
    )

    args = parser.parse_args(argv)
    try:
        validate_options(args.start_port, args.end_port, args.timeout, args.workers)
    except ValueError as error:
        parser.error(str(error))
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    try:
        # Resolve the name once, then connect directly to its IPv4 address.
        ip_address = socket.gethostbyname(args.target)
    except socket.gaierror as error:
        print("Could not resolve target: {}".format(error), file=sys.stderr)
        return 2

    print(
        "Scanning {} ({}) for TCP ports {}-{}...".format(
            args.target, ip_address, args.start_port, args.end_port
        )
    )
    started_at = time.perf_counter()
    open_ports = []
    ports = range(args.start_port, args.end_port + 1)

    # A small thread pool checks several ports at once, so timeouts don't make
    # a typical scan take too long.
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(scan_port, ip_address, port, args.timeout): port
            for port in ports
        }
        for future in as_completed(futures):
            if future.result():
                open_ports.append(futures[future])

    elapsed = time.perf_counter() - started_at
    print("\nScan finished in {:.2f} seconds.".format(elapsed))
    if open_ports:
        print("Open TCP ports:")
        for port in sorted(open_ports):
            print("  {}/tcp open".format(port))
    else:
        print("No open TCP ports found in that range.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
