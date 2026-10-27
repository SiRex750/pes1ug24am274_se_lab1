# Lab 5 – Issue Table

**Student:** Siddanth Anil (PES1UG24AM274, Section E) · **File:** `parcel_tracker.py`
Line numbers refer to the original file (before fixes).

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell injection via `shell=True` (Bandit B602, **High**) | Security | 55 | `pingHub` concatenates the caller's address into a shell string, so `"x; rm -rf ~"` would run arbitrary commands. | Validate the address against a strict hostname/IP regex (must start alphanumeric, so it can't be parsed as an option), resolve `ping` with `shutil.which`, and call `subprocess.check_output([ping, "-c", "1", addr])` with no shell. |
| Insecure temp file `mktemp` (Bandit B306, **Medium**) | Security | 50 | `tempfile.mktemp` only returns a name; another process can create/symlink that path before we use it (race condition). | Use `tempfile.mkstemp`, which atomically creates the file; close the descriptor and return the path. |
| Weak RNG for an OTP (Bandit B311, Low) | Security | 72 | `random.randint` is a predictable Mersenne Twister, unsuitable for a delivery OTP. | `1000 + secrets.randbelow(9000)` (same 1000–9999 range, CSPRNG). |
| `subprocess` import (Bandit B404, Low) | Security | 2 | Informational flag on importing `subprocess`. | Kept (needed for `ping_hub`) and annotated `# nosec B404` with the reason; all calls now use a fixed argv list. |
| Mutable default argument (Pylint W0102) | Bug | 11 | `history=[]` is created once and shared by every call, so ids leak between unrelated callers. | Default to `None`, create a new list inside the function. |
| Overly broad `except Exception` (Pylint W0718) | Bug / Robustness | 37 | Would also swallow unrelated errors (e.g. a `TypeError`) and report them as "Unknown tracking id". | Catch only `KeyError`, the one failure a missing id can cause. |
| Chained `==` comparisons (Pylint R1714) | Refactor | 45 | `status == "Picked Up" or status == "In Transit"` is verbose. | `status in ("Picked Up", "In Transit")`. |
| camelCase names (Pylint C0103 ×15) | Style / Convention | 11–67 | Functions, arguments and variables (`bookParcel`, `trackingId`, `weightKg`…) violate PEP 8 snake_case. | Renamed to `book_parcel`, `tracking_id`, `weight_kg`, etc. and updated every call site. |
| Missing docstrings (Pylint C0114, C0116 ×8) | Documentation | 1, 11–58 | Module and all functions undocumented. | Added a module docstring and a short docstring per function. |
| Missing whitespace around `=` (Flake8 E225) | Style | 28 | `cost=50` | `cost = 50` |
| Inline comment spacing (Flake8 E261) | Style | 71 | One space before `# unknown id`. | Two spaces before inline comment. |
| Missing space after comma (Flake8 E231) | Style | 74 | `print("…:",len(parcels))` | Added space after the comma. |
| No blank lines after function / import side effect (Flake8 E305) | Style / Design | 75 | `main()` called directly after the function, and runs on import. | Two blank lines and `if __name__ == "__main__":` guard. |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 4.91 / 10 (27 messages) | **10.00 / 10** |
| Bandit | 1 High, 1 Medium, 2 Low | **No issues identified** |
| Flake8 | 4 findings | **0** |

Reports are in `reports/` (`*_before.txt` / `*_after.txt`).
