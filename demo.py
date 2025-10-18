"""
This is a demonstration file for the exoanchor tool.

- It is syntactically correct, so `exoanchor syntax demo.py` will pass.
- It uses a feature from an old version of NumPy that is now removed.
- `exoanchor run` will upgrade NumPy and correctly report a failure.
"""
import numpy as np

def check_old_numpy_feature():
    """
    This function uses `np.bool`, which was deprecated and removed in NumPy 1.24.
    """
    print(f"--> Checking with NumPy version: {np.__version__}")
    
    result = np.bool(True)
    
    assert result is True
    print("--> Old NumPy feature check passed.")

if __name__ == "__main__":
    check_old_numpy_feature()