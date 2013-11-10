#!/usr/bin/env python
"""
Simple command-line interface to the Codebase API.  Example usage:

    ./cli.py myproject all_notes 6

Arguments:
1. project name
2. api function name
3. args to pass to the api function
"""
import sys
from client import CodeBaseAPI


def main():
    project = sys.argv[1]
    command = sys.argv[2]
    args = sys.argv[3:]

    codebase = CodeBaseAPI(
        project=project,
    )
    response = getattr(codebase, command)(*args)
    import pprint ; pprint.pprint(response)


if __name__ == "__main__":
    main()
