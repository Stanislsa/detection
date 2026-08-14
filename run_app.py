"""
Point d'entrée principal de l'application desktop SentinelAI.
"""

import os
import sys
from pathlib import Path

# Fix pour conflit DLL Intel OpenMP / PyTorch sous Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

try:
    import torch
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).parent))

from app.desktop.application import Application


def main():
    """Point d'entrée principal de l'application."""
    app = Application()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
