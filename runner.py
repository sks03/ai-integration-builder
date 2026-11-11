import subprocess, sys, os
from safeguards import mask_emails

def run_dry(code_path: str) -> str:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(
            [sys.executable, code_path, "--dry-run"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60, env=env,
        )
    except subprocess.TimeoutExpired:
        return "Run timed out after 60 seconds."
    return mask_emails(result.stdout + "\n" + result.stderr)