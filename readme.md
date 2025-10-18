# 🛡️ exoanchor

**exoanchor: Your anchor in the stormy seas of dependency updates.**

A zero-configuration CLI tool that tells you if your Python project will break *before* you upgrade your dependencies. It also includes a rapid, focused syntax checker to catch common typos before you commit.

## Why?

Ever run `pip install -U ...` and watched your project explode? Or pushed a commit from your phone only to find a simple syntax error broke the build?

`exoanchor` automates the process of finding out if an upgrade is safe and provides a quick, "in-the-moment" sanity check for your code, reducing frustration and saving you time.

## Core Principles

### 🛡️ Secure and Ephemeral by Design

`exoanchor` is built to be a trustworthy guest in your project. It follows a strict "Leave No Trace" policy.

*   **No Persistent Storage:** It does not create any permanent caches, logs, or configuration files.
*   **Complete Sandbox Cleanup:** Every run creates a temporary sandbox folder (`exoanchor_sandbox/`) which is **guaranteed** to be completely deleted after the run finishes, whether it succeeds or fails.
*   **No Side Effects:** The tool never modifies your project's files, `requirements.txt`, or your global Python environment.

You can run `exoanchor` with the confidence that it will not permanently alter your system in any way.

## Getting Started (v0.2.0)

See what `exoanchor` can do in under 60 seconds.

**Prerequisites:** You need Python 3.8+ and Git installed.

### 1. Install `exoanchor`

Clone the repository and install the tool in an isolated environment.

```bash
# Clone the project
git clone https://github.com/YourUsername/exoanchor.git
cd exoanchor

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install exoanchor in editable mode
pip install -e .
```
*(Note: Replace `YourUsername` with your actual GitHub username!)*

### 2. Create the Demo Files

Run the built-in `demo` command. This will create sample files in your current directory and show you the next commands to run.

```bash
exoanchor demo
```

### 3. Run the Checks

Now, run the commands provided by the demo to see `exoanchor` in action.

**Test the syntax checker (this will pass cleanly):**
```bash
exoanchor syntax demo.py
```
**Expected Output:**
```
✅ No syntax errors found!
```

**Test the resilience checker (this will fail, as intended, proving its utility):**
```bash
exoanchor run --reqs demo_requirements.txt --command "python3 demo.py"
```
**Expected Output:**
```
💥 FAILED: Your project broke in the 'LATEST STABLE' scenario.
```

You've just used both core features of `exoanchor` to verify a file's syntax and discover a future dependency breakage.

## Commands Overview

*   `exoanchor run`: The core resilience checker. It creates a sandbox with the latest dependencies and runs your test command inside it.
*   `exoanchor syntax`: A rapid, focused static analysis tool to check a single file for common, blocking syntax errors.
*   `exoanchor demo`: A helper command that creates `demo.py` and `demo_requirements.txt` to let you quickly test the tool.

## Advanced Usage: Automation with JSON

The `run` command supports a `--json` flag to output results in a machine-readable format, perfect for CI/CD pipelines and other scripts.

```bash
exoanchor run --command "pytest" --json > results.json
```

## Known Limitations

*   The `run` command does not yet handle complex `requirements.txt` files (e.g., git URLs, local paths).

## Contributing

This project is just getting started! If this tool seems useful to you, please Star the repository, open an Issue with ideas, or submit a Pull Request.