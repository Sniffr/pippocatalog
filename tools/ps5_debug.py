#!/usr/bin/env python3
"""Check a jailbroken PS5 from your PC and capture the kernel log.

Usage:  python ps5_debug.py <ps5-ip>

1. Checks which payload ports answer (loader, klog, FTP, PS5 Library).
2. Streams the kernel log (port 9081) to the screen and to ps5_klog.txt.
   Launch the failing game on the PS5 while this runs, then press Ctrl+C
   and send ps5_klog.txt (the last ~100 lines) back for review.
"""
import socket
import sys
import time

PORTS = {
    9021: "ELF loader",
    9081: "klog (kernel log)",
    2121: "FTP (ftpsrv)",
    1337: "FTP (alt)",
    9999: "PS5 Library web page",
}


def port_open(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=2):
            return True
    except OSError:
        return False


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ip = sys.argv[1]
    print(f"Checking {ip} ...")
    for port, name in PORTS.items():
        print(f"  {port:5} {name:24} {'OPEN' if port_open(ip, port) else 'closed'}")
    if not port_open(ip, 9081):
        sys.exit("\nklog (9081) is closed. Load a klog payload, then run again.")
    print("\nStreaming klog. Launch the failing game now. Ctrl+C to stop.\n")
    with socket.create_connection((ip, 9081), timeout=5) as s, \
            open("ps5_klog.txt", "ab") as f:
        s.settimeout(None)
        try:
            while True:
                data = s.recv(4096)
                if not data:
                    break
                sys.stdout.write(data.decode(errors="replace"))
                sys.stdout.flush()
                f.write(data)
        except KeyboardInterrupt:
            pass
    print("\nSaved to ps5_klog.txt")


if __name__ == "__main__":
    main()
