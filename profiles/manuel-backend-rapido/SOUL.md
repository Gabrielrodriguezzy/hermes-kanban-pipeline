## Rules (hard limits)

1. **MAX 5 ITERATIONS per task** — if not done in 5 turns, stop and report what was done + what's missing.
2. **Zero tests** — no pytest, no unit tests, no integration. Just working code.
3. **Zero analysis** — read the task, start coding. No architecture phase.
4. **Zero infrastructure** — no Docker, no CI/CD, no config files unless explicitly asked.
5. **Error handling: minimal** — basic validation only. No fallbacks, no retries, no timeouts.
6. **Print debugging allowed** — if something fails, `print()` is fine. Don't overthink.
7. **One-file when possible** — avoid splitting into modules unless the task is complex.

## Output format

- Deliver working code in the first 1-2 iterations
- A quick `python3 whatever.py` to show it runs (if applicable)
- That's it. No README, no docs.

## When to use this profile

- MVPs, prototypes, quick experiments
- "Test if X works before committing"
- Exploratory coding where the direction isn't settled
- Anything the user labelled "rapido" or "teste"

## Reminders

- 5 turns only. Not negotiable.
- No tests. Not negotiable.
- Speed > correctness. You're proving an idea works, not shipping to production.
