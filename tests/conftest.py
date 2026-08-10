import os
import sys

# Empêcher les conflits DLL Intel OpenMP sur Windows avec PyTorch/OpenCV
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

try:
    import torch
except Exception:
    pass
