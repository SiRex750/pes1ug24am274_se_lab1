# Lab 5 – Reflection

**Student:** Siddanth Anil (PES1UG24AM274, Section E)

## 1. Which issues were the easiest and which were the hardest to fix?

Easiest were the mechanical ones: Flake8's whitespace findings, the `in` refactor and the docstrings, each a one-line change with no effect on behaviour. The renames (camelCase to snake_case) were also easy but needed care, since every call site had to change together. The hardest was the `shell=True` command injection in `ping_hub`: deleting `shell=True` was not enough. The address also had to be validated, because a value starting with `-` could still be read as a `ping` option, and the executable had to be located safely. The mutable default argument was the subtlest bug, because the program ran correctly in the demo and only fails when `book_parcel` is called repeatedly without a `history`.

## 2. Did the tools report any false positives, or issues that weren't worth fixing?

Bandit B404 (importing `subprocess`) is informational, not a vulnerability. The module is needed, so I kept it and suppressed the warning with `# nosec B404` and a comment explaining why. The same applies to B603 on the `check_output` call: after validation and removing the shell, the remaining risk is accepted and documented. I treated `nosec` as a recorded decision, not a way to hide the warning. Pylint's missing-docstring warnings felt low-value on tiny helpers, but they were cheap to fix and make the intended behaviour explicit.

## 3. How would you integrate static analysis into your regular development workflow?

Run Flake8 and Pylint locally through a pre-commit hook so style problems never reach a commit, and run all three tools, including Bandit, in CI on each pull request. A failing check, such as a Bandit High or a Pylint score below a threshold, would block the merge. Security findings should be treated as blocking, style findings as auto-fixable (for example with a formatter), and any `nosec`/`disable` comment should need a justification in review.

## 4. What tangible improvements did you observe in the code after applying the fixes?

Pylint went from 4.91 to 10.00, Bandit from one High, one Medium and two Low findings to none, and Flake8 from four findings to none. Beyond the numbers, the code is safer (no shell injection, no temp-file race, an unpredictable OTP), more correct (no shared mutable default, no over-broad `except`), easier to read (consistent naming and docstrings), and importable without side effects because of the `__main__` guard.
