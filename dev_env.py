#!/usr/bin/env python3
"""Environment-backed entrypoint for DEV.to Analytics Pro.

Keeps the DEV.to API key out of the process argument vector while preserving
all existing ``dev.py`` analysis flags.
"""
from __future__ import annotations

import os
import sys

import dev


def main() -> None:
    api_key = os.environ.get("DEVTO_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "DEVTO_API_KEY is not set. Export it in the current shell before running dev_env.py."
        )

    # dev.main() owns the existing argparse interface. Inject the credential
    # into Python's in-memory argv only; it never appears in the OS command line.
    sys.argv[1:1] = ["--api-key", api_key]
    dev.main()


if __name__ == "__main__":
    main()
