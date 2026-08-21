#!/usr/bin/env python3
"""
AVA OS Installation Script

Handles:
- Python dependency installation
- API key setup
- Knowledge base initialization
- Directory structure creation
"""

import sys
import os
import platform
import subprocess
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_step(step_num: int, text: str):
    """Print a step."""
    print(f"[{step_num}] {text}")


def run_command(cmd: list, description: str = "") -> bool:
    """Run a command and return success status."""
    if description:
        print(f"    Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"    Error: {result.stderr}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"    Timeout running command")
        return False
    except Exception as e:
        print(f"    Exception: {e}")
        return False


def check_python():
    """Verify Python version."""
    print_step(1, "Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"    Error: Python 3.9+ required (you have {version.major}.{version.minor})")
        return False
    print(f"    OK: Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Install Python packages."""
    print_step(2, "Installing dependencies...")
    requirements_file = Path(__file__).resolve().parents[1] / "requirements.txt"

    if not requirements_file.exists():
        print(f"    Error: requirements.txt not found at {requirements_file}")
        return False

    cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
    if run_command(cmd, "pip install"):
        print("    OK: Dependencies installed")
        return True
    return False


def setup_api_key():
    """Help user set up Anthropic API key."""
    print_step(3, "Setting up Anthropic API key...")

    # Check if already set
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("    OK: ANTHROPIC_API_KEY already set")
        return True

    print("\n    AVA needs an Anthropic API key for hallucination checking.")
    print("    Get your key from: https://console.anthropic.com/account/keys\n")

    api_key = input("    Enter your API key (or press Enter to skip): ").strip()

    if not api_key:
        print("    WARNING: Skipped API key setup")
        return True

    # Set environment variable
    os.environ["ANTHROPIC_API_KEY"] = api_key

    # Suggest persistent setup
    system = platform.system()
    if system == "Windows":
        print("\n    To make this permanent, set in PowerShell:")
        print(f"    $env:ANTHROPIC_API_KEY = '{api_key}'")
        print("\n    Or set it in Environment Variables (System Properties)")
    else:
        print("\n    To make this permanent, add to ~/.bashrc or ~/.zshrc:")
        print(f"    export ANTHROPIC_API_KEY='{api_key}'")

    print("    OK: API key configured for this session")
    return True


def initialize_knowledge_base():
    """Initialize the knowledge base."""
    print_step(4, "Initializing knowledge base...")

    kb_dir = Path("~/.ava_os/knowledge").expanduser()
    kb_dir.mkdir(parents=True, exist_ok=True)

    # Run knowledge initialization
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root / "src"))

    try:
        from avaos.knowledge_manager import initialize_knowledge_base
        initialize_knowledge_base(kb_dir)
        print("    OK: Knowledge base initialized")
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print_step(5, "Creating directories...")

    dirs = [
        Path("~/.ava_os/memory").expanduser(),
        Path("~/.ava_os/knowledge").expanduser(),
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"    OK: {d}")

    return True


def print_next_steps():
    """Print next steps."""
    print_header("INSTALLATION COMPLETE")
    print("""
Next steps:

1. Start a conversation:
   python -m avaos.chat --voice     (with voice I/O)
   python -m avaos.chat             (text only)

2. Open the parental dashboard:
   python scripts/dashboard.py
   Then open http://localhost:5000 in your browser

3. Manage the knowledge base:
   python scripts/manage_knowledge.py --view-age 10
   python scripts/manage_knowledge.py --add

Files are stored in:
   ~/.ava_os/memory/             (conversation history)
   ~/.ava_os/knowledge/          (knowledge base)

For Docker deployment:
   docker-compose up

Questions or issues?
   Check README.md for more information
""")


def main():
    """Run the installation."""
    print_header("AVA OS Installation")

    steps = [
        ("Python check", check_python),
        ("Install dependencies", install_dependencies),
        ("API key setup", setup_api_key),
        ("Create directories", create_directories),
        ("Initialize knowledge base", initialize_knowledge_base),
    ]

    for i, (name, func) in enumerate(steps, 1):
        if not func():
            print(f"\nInstallation failed at step {i}: {name}")
            print("Please fix the error above and try again.")
            sys.exit(1)

    print_next_steps()
    print("Installation successful! Enjoy AVA OS.\n")


if __name__ == "__main__":
    main()
