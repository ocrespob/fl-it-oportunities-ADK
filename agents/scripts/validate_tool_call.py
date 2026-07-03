# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Validation script for tool calls to prevent destructive command execution."""

import json
import re
import sys


def is_destructive(command: str) -> bool:
    """Inspects a shell command for destructive operations.

    Args:
        command: The command line string.

    Returns:
        True if the command contains destructive patterns, False otherwise.
    """
    cmd = command.strip().lower()

    # Define critical system directories to protect
    critical_folders = [
        "/bin",
        "/boot",
        "/dev",
        "/etc",
        "/home",
        "/lib",
        "/lib64",
        "/media",
        "/mnt",
        "/opt",
        "/proc",
        "/root",
        "/run",
        "/sbin",
        "/srv",
        "/sys",
        "/usr",
        "/var",
    ]

    # List of commands that are safe to contain potentially dangerous strings
    safe_commands = (
        "git",
        "echo",
        "grep",
        "rg",
        "ripgrep",
        "cat",
        "less",
        "more",
    )

    # Split the command by common shell command separators
    subcommands = re.split(r";|&&|\|\||\|", cmd)
    for sub in subcommands:
        sub = sub.strip()
        tokens = sub.split()
        if not tokens:
            continue

        # Find the index of the command (ignoring common prefixes like sudo or env vars)
        cmd_idx = -1
        for idx, token in enumerate(tokens):
            if token == "sudo" or "=" in token:
                continue
            cmd_idx = idx
            break

        if cmd_idx == -1:
            continue

        main_cmd = tokens[cmd_idx]

        # If the main command of this subcommand is in the safe list, skip regex checks
        # to avoid false positives like git commit -m "fix rm -rf /" or grep "rm -rf /"
        if any(
            main_cmd == safe
            or main_cmd.endswith(f"/{safe}")
            or main_cmd.endswith(f"\\{safe}")
            for safe in safe_commands
        ):
            continue

        # 1. Regex checks for this subcommand
        # Match rm -rf / or rm -fr / or rm -r -f / or rm -rfv /
        if re.search(r"\brm\b.*-[a-zA-Z]*[rf][a-zA-Z]*[rf].*\s+/\*?(\s+|$)", sub):
            return True

        # Match rm -rf targeting critical directories
        for critical in critical_folders:
            escaped_critical = re.escape(critical)
            if re.search(
                rf"\brm\b.*-[a-zA-Z]*[rf][a-zA-Z]*[rf].*\s+{escaped_critical}(/|\s+|$)",
                sub,
            ):
                return True

        # Match rm with long flags --recursive and --force
        if "--recursive" in sub and "--force" in sub:
            if re.search(r"\s+/\*?(\s+|$)", sub):
                return True
            for critical in critical_folders:
                escaped_critical = re.escape(critical)
                if re.search(rf"\s+{escaped_critical}(/|\s+|$)", sub):
                    return True

        # 2. Token-based analysis for this subcommand
        if main_cmd == "rm" or main_cmd.endswith("/rm"):
            flags = []
            targets = []
            for token in tokens[cmd_idx + 1 :]:
                if token.startswith("-"):
                    flags.append(token)
                else:
                    targets.append(token)

            is_recursive = False
            is_force = False
            for flag in flags:
                if flag.startswith("--"):
                    if flag == "--recursive":
                        is_recursive = True
                    elif flag == "--force":
                        is_force = True
                elif flag.startswith("-"):
                    for char in flag[1:]:
                        if char in ("r", "R"):
                            is_recursive = True
                        elif char == "f":
                            is_force = True

            if is_recursive and is_force:
                for target in targets:
                    norm_target = target.strip("'\"").rstrip("/")
                    if norm_target == "":
                        return True
                    if norm_target in ("*", "/*", ".", "..", ".*"):
                        return True
                    for critical in critical_folders:
                        if norm_target == critical or norm_target.startswith(
                            critical + "/"
                        ):
                            return True

        # Handle Windows rd / rmdir
        elif main_cmd in ("rd", "rmdir") or any(
            main_cmd.endswith(f"/{c}") or main_cmd.endswith(f"\\{c}")
            for c in ("rd", "rmdir")
        ):
            has_s = False
            has_q = False
            targets = []
            for token in tokens[cmd_idx + 1 :]:
                if token.startswith("/") or token.startswith("-"):
                    t_clean = token.lower().strip("-/")
                    if "s" in t_clean:
                        has_s = True
                    if "q" in t_clean:
                        has_q = True
                else:
                    targets.append(token)

            if has_s and has_q:
                for target in targets:
                    norm_target = target.strip("'\"").lower().replace("/", "\\")
                    if norm_target in (
                        "c:",
                        "c:\\",
                        "c:\\*",
                        "c:\\windows",
                        "%systemroot%",
                        "%windir%",
                    ):
                        return True

        # Handle Windows del / erase
        elif main_cmd in ("del", "erase") or any(
            main_cmd.endswith(f"/{c}") or main_cmd.endswith(f"\\{c}")
            for c in ("del", "erase")
        ):
            has_f = False
            has_s = False
            has_q = False
            targets = []
            for token in tokens[cmd_idx + 1 :]:
                if token.startswith("/") or token.startswith("-"):
                    t_clean = token.lower().strip("-/")
                    if "f" in t_clean:
                        has_f = True
                    if "s" in t_clean:
                        has_s = True
                    if "q" in t_clean:
                        has_q = True
                else:
                    targets.append(token)

            if has_f and has_s and has_q:
                for target in targets:
                    norm_target = target.strip("'\"").lower().replace("/", "\\")
                    if norm_target in (
                        "c:",
                        "c:\\",
                        "c:\\*",
                        "c:\\windows",
                        "%systemroot%",
                        "%windir%",
                    ):
                        return True

    return False


def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)
        data = json.loads(input_data)
    except Exception as e:
        print(f"Error parsing stdin: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name == "run_command":
        command = (
            tool_input.get("CommandLine")
            or tool_input.get("commandLine")
            or tool_input.get("command", "")
        )

        if command and is_destructive(command):
            reason = (
                f"Command execution blocked: '{command}' matches destructive"
                " patterns."
            )
            response = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
            print(json.dumps(response))
            print(reason, file=sys.stderr)
            sys.exit(2)

    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
        }
    }
    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
