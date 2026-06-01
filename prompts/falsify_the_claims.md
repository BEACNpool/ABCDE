# Falsify The Claims

Act as a skeptical reviewer of the ABCDE repository.

Use local committed data only unless a GitHub Release bundle has been fetched
and verified. Your job is to find ways the public claims could be wrong.

Checklist:

1. Run `python scripts/verify_claim_receipts.py`.
2. Identify any claim whose SQL does not directly prove the wording.
3. Look for double counting, stale timestamps, missing source hashes, row-count
   mismatches, and ambiguous labels.
4. Separate data problems from interpretation problems.
5. Propose tighter claim wording where the evidence does not support the
   stronger version.

Output sections: FINDINGS, UNCERTAINTY, BETTER WORDING, QUERIES RUN.
