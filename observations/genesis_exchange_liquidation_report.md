# Genesis Allocation: Liquidation to Exchange Heuristics

**Query Reference:** ABCDE Database - Exchange Identification Layer

## Methodology
This report quantifies the volume of traced genesis ADA that terminated in known or highly-probable centralized exchange addresses. 
The exchange roster was built using a combination of explicit on-chain labels (e.g., Binance) and high-confidence behavioral heuristics (addresses with >10,000 transactions, >1,000 distinct senders, and zero staking history). The traced frontiers of IOG, EMURGO, and the Cardano Foundation (CF) were then intersected with this roster.

## Data Output 1: Liquidation Intersection Totals
The following table details the total ADA from the traced genesis frontiers that flowed into the identified exchange roster.

| Genesis Entity | Traced Frontier Total | Sent to Exchanges | % of Frontier Liquidated |
| :--- | :--- | :--- | :--- |
| **EMURGO** | 25.93 Billion ADA | 10.74 Billion ADA | 41.4% |
| **CF** | 14.40 Billion ADA | 4.61 Billion ADA | 32.0% |
| **IOG** | 14.02 Billion ADA | 1.19 Billion ADA | 8.5% |
| **Total** | **54.35 Billion ADA** | **16.54 Billion ADA** | **30.4%** |

## Data Output 2: Top Absorbing Exchange Addresses
The following table highlights the specific exchange-behavior addresses that absorbed the largest quantities of the traced genesis allocations. 

| Address (Truncated) | Genesis Seeds Hit | Total ADA Absorbed | Era / Status |
| :--- | :--- | :--- | :--- |
| `Ae2tdPwUPEYwFx4d...` | CF, EMURGO | 6.64 Billion | Byron (Probable Exchange) |
| `Ae2tdPwUPEZ5ZFno...` | CF, EMURGO | 2.46 Billion | Byron (Probable Exchange) |
| `Ae2tdPwUPEZ5faoe...` | CF, EMURGO, IOG | 2.16 Billion | Byron (Probable Exchange) |
| `addr1q8elqhkuv...` | EMURGO Only | 628 Million | Shelley (Probable Exchange) |
| `Ae2tdPwUPEZ6xYrx...` | CF, EMURGO, IOG | 628 Million | Byron (Probable Exchange) |
| `DdzFFzCqrhstmq...` | CF, EMURGO, IOG | 363 Million | Byron (Very High Confidence) |
| `DdzFFzCqrhskEmd...` | EMURGO, IOG | 215 Million | Byron (Confirmed Binance) |

**Note:** The top three addresses absorbed ~11.26 Billion ADA combined and operated as shared destination hubs for multiple founding entities.
