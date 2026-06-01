# Public Claim Receipts

This directory turns headline repo claims into reproducible SQL receipts.

Run:

```bash
python scripts/verify_claim_receipts.py
```

Each receipt has:

- a plain-English claim
- an evidence grade
- a SQL file under `claims/sql/`
- expected row count
- SHA-256 of the TSV-rendered result

These receipts are not a substitute for a professional audit. They are a compact
way for a cloned repo plus an AI agent to verify that public figures are grounded
in committed data.
