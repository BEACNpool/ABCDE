# Genesis Allocation: Exchange-Classified Frontier Intersection

**Query Reference:** ABCDE Database - Exchange Identification Layer

## Methodology
This report quantifies the volume of traced frontier ADA that intersects a published exchange-identification layer.
The exchange roster was built using a combination of explicit on-chain labels (e.g., Binance) and high-confidence behavioral heuristics (addresses with >10,000 transactions, >1,000 distinct senders, and zero staking history). The traced frontiers of IOG, EMURGO, and the Cardano Foundation (CF) were then intersected with this roster.

**Scope note:** This report reflects the currently published combined frontier classification for **IOG + EMURGO + CF**. `EMURGO_2` is not included in this observation.

**Interpretation note:** Values in this report represent **exchange-classified frontier intersections**, not a complete proof of realized sale volume, ownership, beneficiary identity, or intent.

## Data Output 1: Exchange-Classified Frontier Totals
The following table details the total ADA from the traced genesis frontiers that intersect the identified exchange roster.

| Genesis Entity | Traced Frontier Total | Exchange-Classified Frontier Value | % of Frontier in Exchange Bucket |
| :--- | :--- | :--- | :--- |
| **EMURGO** | 25.93 Billion ADA | 10.74 Billion ADA | 41.4% |
| **CF** | 14.40 Billion ADA | 4.61 Billion ADA | 32.0% |
| **IOG** | 14.02 Billion ADA | 1.19 Billion ADA | 8.5% |
| **Total** | **54.35 Billion ADA** | **16.54 Billion ADA** | **30.4%** |

## Data Output 2: Top Exchange-Classified Addresses
The following table highlights specific addresses in the exchange-identification layer that intersect the largest quantities of the traced genesis frontiers. 

| Address (Truncated) | Genesis Seeds Hit | Total ADA Absorbed | Era / Status |
| :--- | :--- | :--- | :--- |
| `Ae2tdPwUPEYwFx4d...` | CF, EMURGO | 6.64 Billion | Byron (Probable Exchange) |
| `Ae2tdPwUPEZ5ZFno...` | CF, EMURGO | 2.46 Billion | Byron (Probable Exchange) |
| `Ae2tdPwUPEZ5faoe...` | CF, EMURGO, IOG | 2.16 Billion | Byron (Probable Exchange) |
| `addr1q8elqhkuv...` | EMURGO Only | 628 Million | Shelley (Probable Exchange) |
| `Ae2tdPwUPEZ6xYrx...` | CF, EMURGO, IOG | 628 Million | Byron (Probable Exchange) |
| `DdzFFzCqrhstmq...` | CF, EMURGO, IOG | 363 Million | Byron (Very High Confidence) |
| `DdzFFzCqrhskEmd...` | EMURGO, IOG | 215 Million | Byron (Confirmed Binance) |

**Note:** The top three addresses intersect ~11.26 Billion ADA combined in the published exchange-identification layer. Address-level labels should be read as heuristic / roster-based classifications unless separately supported by explicit published labels.
