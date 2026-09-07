#!/usr/bin/env python3
"""Compatibility entrypoint for the provider-neutral conformance runner.

The implementation lives in :mod:`run_conformance`; this file remains only so
existing scripts fail over to the new explicit remote-provider contract.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_conformance import *  # noqa: F401,F403,E402


if __name__ == "__main__":
    raise SystemExit(main())
