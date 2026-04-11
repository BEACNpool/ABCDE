# EMURGO_2 Public Disclosure Search
**Date:** 2026-04-08
**Scope:** Determine whether the `781,381,495 ADA` amount tied on-chain to `5ec95a53...` was publicly disclosed, and if so, in what form.

## Database Load Status

The reference-table load was **not completed** from this workstation.

- Attempted connection to `${DB_HOST}:5432` as `codex_audit`
- Server response: `FATAL: no pg_hba.conf entry for host "${DB_HOST}", user "codex_audit", database "cexplorer_replica"`
- Result: the `postgres` superuser load cannot be run from this host until the server allows this client IP or the command is executed from an already authorized machine

## Public Source Findings

### 1. Official named tokenomics narrative still states only one EMURGO allocation

Current public Cardano genesis documentation states:

- Technical and Business Development Pool: `5,185,414,108 ADA`
- Cardano Foundation: `648,176,761 ADA`
- EMURGO: `2,074,165,644 ADA`
- IOHK: `2,463,071,701 ADA`

Source:

- `https://cardano.org/genesis/`
- `https://github.com/cardano-foundation/cardano-org/blob/staging/src/pages/genesis.js`

This is the public narrative presentation of founder-related allocations.

### 2. The exact `781,381,495 ADA` amount was publicly visible in official sale statistics before launch

In the official archived ada sale stats preserved in the `cardano.org` site source, the exact amount `781381495` appears as the maximum ADA amount in multiple categories, including:

- `Tickets / Tranche 4`
- `Tickets / Region / Japan`
- `Tickets / User type / Company`
- `Tickets / Currency / BTC`
- `Tickets / All / All`
- `Buyers / User type / Company / All`

The archived dataset carries an update timestamp of `2017-08-28T15:23:53.138Z`.

Source:

- `https://github.com/cardano-foundation/cardano-org/blob/staging/static/archive/static.iohk.io/adasale/js/stats/main2.json`

This means the **amount itself was publicly exposed in official Cardano sale data before mainnet launch**.

### 3. The exact `781,381,495 ADA` amount was also public in official genesis files before mainnet launch

The official `input-output-hk/cardano-sl` repository contains an AVVM/genesis entry for the exact amount and address:

- AVVM address: `Mutep7fz4IHpNS1eHXnQRPJOmciz9ql1QJF9IAt4XBY=`
- Amount: `781381495000000` lovelace

Verified public appearances:

- `scripts/avvm-files/avvm-utxo.json` in commit `3e9264363e17398930ac87b5b52dd9b6e6b512d0` dated `2017-09-15T19:25:42+03:00`
- `node/configuration.yaml` in commit `ad2a7447d6420cd1f2aa89fbfd03a838bab48769` dated `2017-09-22T20:46:11+03:00`
- `node/mainnet-genesis.json` in commit `08b9017e46108778294870fb80fc78e5287c700e` dated `2017-09-26T20:38:15+03:00`

Sources:

- `https://github.com/input-output-hk/cardano-sl/blob/3e9264363e17398930ac87b5b52dd9b6e6b512d0/scripts/avvm-files/avvm-utxo.json#L4943`
- `https://github.com/input-output-hk/cardano-sl/blob/ad2a7447d6420cd1f2aa89fbfd03a838bab48769/node/configuration.yaml`
- `https://github.com/input-output-hk/cardano-sl/blob/08b9017e46108778294870fb80fc78e5287c700e/node/mainnet-genesis.json`

This means the **genesis entry itself was publicly visible in official code before launch**, but as an unlabeled address entry rather than a named EMURGO allocation.

### 4. No public official source found that attributes this amount to EMURGO

Searches across:

- `cardano.org`
- `iohk.io`
- `emurgo.io`
- `cardanofoundation.org`
- official `cardano-org` and `cardano-sl` repositories

found:

- public presentation of the exact amount
- public presentation of the unlabeled AVVM/genesis address
- **no official source found that explicitly links `781,381,495 ADA` or `Mutep7fz4...` to EMURGO**

## Assessment

The strongest defensible conclusion is:

> The `781,381,495 ADA` amount was public before launch in official sale statistics and genesis files, but I found no official public source that attributes that amount to EMURGO or includes it in the named EMURGO allocation narrative.

That makes these claims materially different:

- **Not supported by this search:** "The `781,381,495 ADA` amount was never public."
- **Supported by this search:** "The public tokenomics narrative named only `2,074,165,644 ADA` for EMURGO and did not publicly attribute the separate `781,381,495 ADA` entry to EMURGO."

## Recommended Revision To Current Framing

If the on-chain overlap evidence remains valid, the lead claim should be tightened from:

- `EMURGO_2 undisclosed allocation`

to something closer to:

- `Publicly visible genesis/sale entry later linked on-chain to the same downstream EMURGO-controlled cluster, but not publicly attributed to EMURGO in the tokenomics narrative`

## Follow-Up Work

- Prove whether the `781,381,495 ADA` entry was a sale-purchased voucher allocation versus a Technical and Business Development Pool allocation
- Tie AVVM address `Mutep7fz4...` to redemption tx `5ec95a53...` in a source-ready write-up
- Re-grade `F01` in `outputs/FULL_FINDINGS_2026-04-06.md` after deciding whether the claim is about:
  - amount visibility
  - entity attribution
  - founder tokenomics narrative omission
