# F18 — SecondFi / Yoroi wallet incident (Cardano-side facts)

## Claim

The June 2026 SecondFi (formerly Yoroi) wallet key-compromise incident is reproduced
from Cardano mainnet as queryable `secondfi_incident_*` tables. What the chain shows:

- Every drain is an ordinary **key-signed** transaction (0 Plutus redeemers, 0 scripts):
  **key compromise, not a Cardano contract or protocol exploit.**
- **`old_fee_sponsored` cluster:** **12,193,786.557442 ADA** confirmed moved to attacker
  collector wallets (`$cybermuna` / `$adanerone` / `$555888`) over 240 transactions,
  2026-06-21 20:29:41 → 06-22 00:35:49 UTC, then routed onward through Cardano DeFi/DEX
  script pools; the collectors were emptied by 2026-06-22.
- A separate **second-attacker collection wallet** holds **4,020,736.95 ADA** (never emptied).
- **`new_william_direct` cluster:** **129,438,872.69 ADA** swept/consolidated over 2,853
  transactions (2026-06-22 → 06-23) into one holding wallet; **129,429,998.977070 ADA** now
  sits in a single vault with **zero outflows since 2026-06-25**.
- An address publicly presented as the incident **recovery fund** received
  16,102,383.735435 ADA and has paid out ~15 ADA at snapshot.
- Both clusters' operational wallets were first funded from the **same community-tagged
  exchange (Binance) omnibus** `addr1vx7j284mqe59w2mka36gf5xq0hvu8ms2989553fk5qh3prcapfpj3`.
- **Key-exposure census (aggregate):** of 3,063 candidate stakes checked, **2,588 were
  cryptographically confirmed exposed** (84.49%), broken down per ring.

## Grade

- **FACT:** all transaction counts, windows, amounts, current balances, spend counts, and
  the aggregate exposure census — reproduced directly from ABCDE/db-sync and shipped as the
  `secondfi_incident_*` tables.
- **STRONG_INFERENCE:** the attacker/collector roles; the DeFi-script laundering route; the
  shared-omnibus funding link (a shared exchange address — not proof of one operator); the
  Binance tag on that omnibus.
- **UNRESOLVED / UNKNOWN (explicitly not established here):** the **intent** of the ~129.4M
  `new_william_direct` sweep (malicious drain vs. protective consolidation) — it is labeled
  neutrally as *swept / consolidated / held*, never as confirmed theft; the real-world
  **identity** of any wallet operator; and any off-chain attribution, motive, or accountability.

## Safety / handling rules (hard constraints)

- **The key-exposure census is AGGREGATE-ONLY.** The per-wallet list of exposed stakes is
  **withheld**; no victim addresses appear in any table; no private-key material is derived or
  published. Publishing which wallets are cryptographically exposed would be a targeting list.
- **The ~129.4M cluster is labeled by what the chain shows** (swept / consolidated / held).
  Intent is UNRESOLVED and must not be rendered as "stolen" without the resolver firing
  (a transfer to a named/audited custodian, or laundering/dispersal).

## Evidence

- **Query-ready tables (clone-and-ask, no node):** `secondfi_incident_summary`,
  `secondfi_incident_actors`, `secondfi_incident_balances`, `secondfi_incident_clusters`,
  `secondfi_incident_theft_destinations`, `secondfi_incident_funding`,
  `secondfi_incident_key_exposure_census`.

## Reproduce

Balances/spend-counts are direct queries against Cardano db-sync at the recorded snapshot
(`secondfi_incident_summary`: `snapshot_block` / `snapshot_time_utc`). The exposure census is
the aggregate of the key-exposure detector run over scoped transaction CBOR; the aggregate is
public, the raw per-wallet output is withheld.
