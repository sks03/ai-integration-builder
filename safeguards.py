import re

ALLOWED_HOSTS = {"api.calendly.com", "auth.calendly.com"}

def static_checks(code: str) -> dict:
    issues = []
    lines = [l for l in code.splitlines() if not l.strip().startswith("#")]
    body = "\n".join(lines)
    if re.search(r"requests\.(post|put|patch|delete)|\.(post|put|patch|delete)\(", body, re.I):
        issues.append("Non-GET HTTP call found")
    if re.search(r"(api[_-]?key|token|secret)\s*=\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]", body, re.I):
        issues.append("Possible hardcoded secret")
    hosts = set(re.findall(r"https?://([A-Za-z0-9\.\-]+)", body))
    bad = sorted(h for h in hosts if h not in ALLOWED_HOSTS)
    if bad:
        issues.append(f"Unexpected hosts: {bad}")
    return {"passed": not issues, "issues": issues}

def mask_emails(text: str) -> str:
    return re.sub(r"([A-Za-z0-9])[A-Za-z0-9_.+-]*@", r"\1***@", text)