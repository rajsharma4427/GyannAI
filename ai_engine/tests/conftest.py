"""
Pytest configuration for ai_engine tests.
"""

import os
import sys
from pathlib import Path

# Ensure GyannAI root is on sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Force mock mode for offline testing
os.environ["AI_MOCK"] = "1"
