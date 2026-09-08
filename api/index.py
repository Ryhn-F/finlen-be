import os
import sys
from pathlib import Path

# Locate the root directory and src directory
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"

# Inject src directory into sys.path so finlen_be is importable in serverless environments
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from finlen_be.main import app

# Expose app for Vercel Serverless Function runtime
__all__ = ["app"]
