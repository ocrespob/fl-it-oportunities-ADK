import ast
import os
import subprocess
import sys


class SecurityVisitor(ast.NodeVisitor):
    def __init__(self, filepath):
        self.filepath = filepath
        self.findings = []

    def visit_Call(self, node):
        # Check for eval() and exec()
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                self.findings.append(
                    {
                        "file": self.filepath,
                        "line": node.lineno,
                        "col": node.col_offset,
                        "id": f"security-gate-use-of-{node.func.id}",
                        "message": f"Avoid using {node.func.id}() due to code execution risks.",
                    }
                )

        # Check for subprocess.run/Popen with shell=True
        elif isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            if node.func.value.id == "subprocess" or node.func.id in (
                "run",
                "Popen",
                "call",
                "check_call",
                "check_output",
            ):
                for keyword in node.keywords:
                    if (
                        keyword.arg == "shell"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        self.findings.append(
                            {
                                "file": self.filepath,
                                "line": node.lineno,
                                "col": node.col_offset,
                                "id": "security-gate-subprocess-shell-true",
                                "message": "Avoid subprocess calls with shell=True due to command injection risks.",
                            }
                        )
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Check for hardcoded secrets
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id.lower()
                if any(
                    x in name
                    for x in ("secret", "password", "api_key", "token", "passwd")
                ):
                    if isinstance(node.value, ast.Constant) and isinstance(
                        node.value.value, str
                    ):
                        val = node.value.value.strip()
                        if len(val) > 4:  # Ignored short dummy values
                            self.findings.append(
                                {
                                    "file": self.filepath,
                                    "line": node.lineno,
                                    "col": node.col_offset,
                                    "id": "security-gate-hardcoded-secret",
                                    "message": f"Potential hardcoded secret assigned to '{target.id}'.",
                                }
                            )
        self.generic_visit(node)

    def visit_Constant(self, node):
        # Check for hardcoded Google API key prefixes (matching AIzaSy[A-Za-z0-9_\-]*)
        if isinstance(node.value, str):
            import re
            if re.search(r'AIzaSy[A-Za-z0-9_\-]*', node.value):
                self.findings.append(
                    {
                        "file": self.filepath,
                        "line": node.lineno,
                        "col": node.col_offset,
                        "id": "detect-google-api-key",
                        "message": "Security Warning: Hardcoded Google API key or prefix detected. Exposing Google API keys in python files poses a significant security risk. Use environment variables or a secrets manager instead.",
                    }
                )
        self.generic_visit(node)



def run_windows_mock(files):
    all_findings = []
    python_files = [f for f in files if f.endswith(".py")]

    print(
        f"Running Windows-Compatible Security Scan on {len(python_files)} python files..."
    )

    for filepath in python_files:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=filepath)
            visitor = SecurityVisitor(filepath)
            visitor.visit(tree)
            all_findings.extend(visitor.findings)
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")

    if all_findings:
        print("\n[SECURITY GATE TRIGGERED] Findings detected:")
        for f in all_findings:
            print(
                f"  - {f['file']}:{f['line']}:{f['col']} -> {f['id']}: {f['message']}"
            )
        print("\nScan failed due to security rule violations.")
        return 1

    print("No security violations found. Scan passed!")
    return 0


def main():
    # If not on Windows, delegate to the actual installed semgrep executable
    if sys.platform != "win32":
        try:
            cmd = ["semgrep", *sys.argv[1:]]
            result = subprocess.run(cmd)
            sys.exit(result.returncode)
        except Exception as e:
            print(f"Failed to delegate to semgrep: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # On Windows: filter arguments to find target files
        files = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

        # If no files are passed, find python files in standard source locations
        if not files:
            files = []
            for root, _, filenames in os.walk("."):
                if ".venv" in root or ".git" in root or ".pytest_cache" in root:
                    continue
                for filename in filenames:
                    if filename.endswith(".py"):
                        files.append(os.path.join(root, filename))

        sys.exit(run_windows_mock(files))


if __name__ == "__main__":
    main()
