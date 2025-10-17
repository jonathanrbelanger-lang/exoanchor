# 🛡️ exoanchor

**exoanchor: Your anchor in the stormy seas of dependency updates.**

A zero-configuration CLI tool that tells you if your Python project will break *before* you upgrade your dependencies.

## Why?

Ever run `pip install -U ...` and watched your project explode? `exoanchor` automates the process of finding out if an upgrade is safe by testing your code against the latest stable versions of your dependencies in a secure, isolated sandbox.

## Core Principles

### 🛡️ Secure and Ephemeral by Design

`exoanchor` is built to be a trustworthy guest in your project. It follows a strict "Leave No Trace" policy.

*   **No Persistent Storage:** It does not create any permanent caches, logs, or configuration files.
*   **Complete Sandbox Cleanup:** Every run creates a temporary sandbox folder (`exoanchor_sandbox/`) which is **guaranteed** to be completely deleted after the run finishes, whether it succeeds or fails.
*   **No Side Effects:** The tool never modifies your project's files, `requirements.txt`, or your global Python environment.

You can run `exoanchor` with the confidence that it will not permanently alter your system in any way.

## Getting Started (v0.1.0)

**STATUS:** ✅ **Ready for Launch!** The core logic is complete and functional for Linux, macOS, and Windows (via WSL).

Since the project isn't on the Python Package Index (PyPI) yet, you can't `pip install` it. Instead, you can install and run it directly from this source code.

**Prerequisites:** You need Python 3.8+ and Git installed.

### 1. Clone the Repository

First, download the project to your computer using `git`.

```bash
git clone https://github.com/YourUsername/exoanchor.git
cd exoanchor
```
*(Note: Replace `YourUsername` with your actual GitHub username!)*

### 2. Set Up a Virtual Environment

Create an isolated Python environment to install `exoanchor` without affecting your system.

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it (you must do this every time you open a new terminal)
source .venv/bin/activate
```

### 3. Install exoanchor in Editable Mode

This command installs `exoanchor` and makes the `exoanchor` command available in your terminal. The `-e` flag means any changes you make to the code are immediately reflected.

```bash
pip install -e .
```

### 4. Run a Demo Test

Let's prove it works! We'll create a quick test case right here in the project folder.

**Create a `requirements.txt` file with an old version of NumPy:**
```bash
echo "numpy==1.20.0" > requirements.txt
```

**Create a `test_script.py` that uses a feature removed in newer NumPy versions:**
```bash
echo 'import numpy as np; print("Testing numpy version:", np.__version__); assert np.bool(True) == True' > test_script.py
```

**Now, run `exoanchor` against this test case:**
```bash
exoanchor --command "python3 test_script.py"
```

### 5. See the Result!

`exoanchor` will find the latest version of NumPy, install it in a temporary sandbox, and run your script. Because the old feature is removed, the script will fail, and `exoanchor` will correctly report it:

```
💥 FAILED: Your project broke in the 'LATEST STABLE' scenario.
```

You've just proven that an upgrade would break your code, without ever changing your actual project files!

## Known Limitations

*   Does not yet handle complex `requirements.txt` files (e.g., git URLs, local paths).

## Contributing

This project is just getting started! If this tool seems useful to you, please Star the repository, open an Issue with ideas, or submit a Pull Request.