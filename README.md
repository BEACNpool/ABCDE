# ABCDE: A BEACN Cardano Data Explorer

**Purpose:** Public archive of Cardano blockchain datasets derived from db-sync chain data.

**Maintained by:** [BEACNpool](https://beacnpool.github.io) (Ticker: BEACN)

---

## Repository Contents

### Datasets

- **[genesis-founders](./datasets/genesis-founders/)** — Transaction lineage traces for Cardano Genesis founder allocations (IOG, Emurgo, Cardano Foundation)

---

## Data Provenance

All datasets in this repository are derived from:
- **Source:** Cardano db-sync PostgreSQL database
- **Sync state:** Block 13,215,210 (2026-03-28 00:27:10 UTC)
- **Method:** Direct SQL queries against replicated chain data
- **Reproducibility:** SQL queries and methodology documented per dataset

---

## Data Integrity

All data files:
- Contain only on-chain verifiable facts
- Include transaction hashes for independent verification
- Can be reproduced by querying db-sync with provided methodology
- Are provided in standard CSV/JSON formats

---

## Usage

This data is public domain (CC0). Use it for:
- Independent verification
- Research and analysis
- Building dashboards and tools
- Auditing blockchain activity

**No warranty provided.** Verify all data independently before relying on it.

---

## Contributing

To suggest corrections or additions:
1. Open an issue with specific transaction hash or data point in question
2. Provide db-sync query that shows different result
3. Include block height and sync timestamp of your query

---

## License

CC0 1.0 Universal — Public Domain

See [LICENSE](./LICENSE) for details.

## Claim Strength

Use this repo with the following claim-strength distinctions in mind:
- **Direct on-chain fact** — directly queryable from db-sync
- **Deterministic transform** — reproducible calculation from published data
- **Heuristic classification** — rule-based label, not direct proof of ownership, sale, or intent
- **Interpretive assessment** — hypothesis or inference based on observed patterns

## On-Chain Observations
* [IOG Genesis Allocation: Output Generation & Routing (Epochs 245-252)](./observations/iog_epoch_245_252_output_routing.md)
* [Genesis Fee Extraction Report](./observations/genesis_fee_extraction_report.md)
* [Genesis Allocation: Liquidation to Exchange Heuristics](./observations/genesis_exchange_liquidation_report.md)

---
**Disclaimer:** *This repository provides raw on-chain data traces mapping the chain of custody for Cardano genesis allocations. We do not provide commentary, assign intent, or draw conclusions on entity behavior. The data is provided as-is for community verification.*
