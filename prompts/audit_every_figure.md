# Audit Every Figure

You are auditing the cloned ABCDE repository. Use the local `abcde-genesis` MCP
server or the committed DuckDB database. Do not use private context, web
searches, or unstated assumptions.

Tasks:

1. Run `list_tables()` and inspect the schema for every table used.
2. Run `python scripts/verify_claim_receipts.py` and report pass/fail.
3. For each claim in `claims/manifest.json`, read the SQL, run it, and explain
   what the result proves and what it does not prove.
4. Cross-check the headline reports against committed tables where possible.
5. Label every statement as FACT, STRONG_INFERENCE, WORKING_HYPOTHESIS, or
   UNKNOWN using `docs/02_GRADING.md`.
6. Explicitly flag any figure that depends on missing release assets or private
   db-sync access.

Hard rule: never infer off-chain ownership, intent, misconduct, or wallet
control from trace/delegation data alone.
