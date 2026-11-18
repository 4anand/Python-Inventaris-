"""Entry point: python main.py [--batch] [-i FILE] [-o FOLDER]"""
import sys

from inventaris.cli import main

if __name__ == "__main__":
    sys.exit(main())
