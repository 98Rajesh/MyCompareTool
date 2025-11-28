#!/usr/bin/env python3
"""
Git wrapper for BC-Lite.
Acts as both difftool and mergetool.

Exit codes:
- 0: success (diff viewed or merge saved)
- non-zero: error or merge cancelled
"""
import os
import sys
import subprocess
from pathlib import Path

BC_LITE_EXEC = None  # Set to packaged binary path if desired

def launch_and_wait(args):
    if BC_LITE_EXEC:
        cmd = [BC_LITE_EXEC] + args
    else:
        cmd = [sys.executable, str(Path(__file__).parent / "main.py")] + args
    try:
        return subprocess.call(cmd)
    except Exception as e:
        print(f"git_wrapper: failed to launch BC-Lite: {e}", file=sys.stderr)
        return 1

def main():
    argv = sys.argv[1:]
    env = os.environ

    # difftool mode: two explicit args
    if len(argv) >= 2:
        left, right = argv[0], argv[1]
        rc = launch_and_wait(["--git-diff", left, right])
        sys.exit(rc if rc is not None else 1)

    # mergetool via env vars
    local = env.get("LOCAL") or env.get("LOCAL_FILE")
    remote = env.get("REMOTE") or env.get("REMOTE_FILE")
    base = env.get("BASE") or env.get("BASE_FILE")
    merged = env.get("MERGED") or env.get("MERGED_FILE")

    if local and remote and merged:
        args = ["--git-merge", "--local", local, "--remote", remote, "--merged", merged]
        if base:
            args += ["--base", base]
        rc = launch_and_wait(args)
        sys.exit(rc if rc is not None else 1)

    # fallback environment-style difftool
    left = env.get("GIT_DIFF_LEFT")
    right = env.get("GIT_DIFF_RIGHT")
    if left and right:
        rc = launch_and_wait(["--git-diff", left, right])
        sys.exit(rc if rc is not None else 1)

    print("git_wrapper: no usable arguments or env vars.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
