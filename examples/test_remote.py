
import sys
import os
import json
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    import nanohubremote
    print(f"nanohubremote version: {getattr(nanohubremote, '__version__', 'unknown')}")
    print(f"Session dir: {dir(nanohubremote.Session)}")
except ImportError:
    print("nanohubremote not found")

