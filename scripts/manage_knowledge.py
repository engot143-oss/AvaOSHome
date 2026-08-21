#!/usr/bin/env python3
"""
Parent tool for managing AVA's knowledge base.

Usage:
  python scripts/manage_knowledge.py --init       # initialize knowledge base
  python scripts/manage_knowledge.py --view-age 10   # see what's available for age 10
  python scripts/manage_knowledge.py --learned    # see what she's learned
  python scripts/manage_knowledge.py --add        # add a new fact interactively
"""

import sys
from pathlib import Path

# Add src to path so we can import avaos modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from avaos.knowledge_manager import (
    initialize_knowledge_base,
    show_knowledge_for_age,
    show_learned_topics,
    add_custom_fact,
)


def main():
    kb_dir = Path("~/.ava_os/knowledge").expanduser()

    if len(sys.argv) < 2:
        print("AVA Knowledge Base Manager")
        print("\nUsage:")
        print("  python scripts/manage_knowledge.py --init          Initialize knowledge base")
        print("  python scripts/manage_knowledge.py --view-age N    Show facts for age N")
        print("  python scripts/manage_knowledge.py --learned       Show what she's learned")
        print("  python scripts/manage_knowledge.py --add           Add a new fact")
        return

    cmd = sys.argv[1]

    if cmd == "--init":
        initialize_knowledge_base(kb_dir)
    elif cmd == "--view-age":
        age = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_knowledge_for_age(kb_dir, age)
    elif cmd == "--learned":
        show_learned_topics(kb_dir)
    elif cmd == "--add":
        add_custom_fact(kb_dir)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
