#!/usr/bin/env python3
"""
Launch the AVA OS parental dashboard.

Usage:
  python scripts/dashboard.py          # Start on default port 5000
  python scripts/dashboard.py --port 8080  # Start on custom port
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.dashboard import DashboardServer


def main():
    port = 5000

    # Parse command line args
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    server = DashboardServer(port=port)
    server.run(debug=False)


if __name__ == "__main__":
    main()
