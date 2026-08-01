# oligarCH — the maker, the gate, and the wall

The ninth piece of the **oligarCH** series is not a drawing. It is a **maker**: a wizard that lets a
holder assemble their own oligarCH and mint it, with the picture itself living **inside the minting
transaction**. No IPFS, no pinning, no CDN, no server holding the art.

This repository is the whole thing — the Plutus validator, the SVG builder, the page that signs in
the browser, the wall that reads the chain, and the test harnesses that prove it.

> **Live:** <https://beacnpool.github.io/ABCDE/oligarCH/>
> **Make one:** <https://beacnpool.github.io/ABCDE/oligarCH/make/>
> **The wall:** <https://beacnpool.github.io/ABCDE/oligarCH/make/wall/>

---

## The contract

Five properties that do not change:

1. **The image lives entirely in the minting transaction.** SVG → base64 data URI → 64-byte
   metadata chunks under label `721`. Pull any mint apart and the artwork comes back byte-identical.
2. **No payment output.** The minter pays their own network fee and nothing else. The creator
   receives nothing, and there are no royalties (no CIP-27 token under any policy here).
3. **Seed-UTxO uniqueness.** The asset name carries the first 8 hex of the seed UTxO's transaction,
   and the seed is consumed by the mint — so a name can never repeat.
4. **A static page that signs in the browser** via CIP-30. There is no backend.
5. **The eight are a bare timelock; the ninth is a holdings gate.** Details below.

## Series one — the eight

Eight memes, each drawn inside a measured byte ceiling, each minted under its own **bare timelock
policy** (`{"type":"before","slot":N}`) with no key witness. That single choice makes each piece
open, free and time-boxed at once: anyone may mint until the slot, and after it **nothing can ever
be minted or burned under that policy again** — including by the creator.

| # | ticker | phrase | policy id |
|---|--------|--------|-----------|
| 1 | `BYTTG` | BURN YOU TO THE GROUND | `2ef849a4e7742f0705f41c7b2195bb828b934ee48dcfa0c204ae2a8d` |
| 2 | `TGM`   | THE GREAT MIGRATION    | `7ba4e6b009013f83cae317390fd88c1b734154cc110ab1b31fbc4ac5` |
| 3 | `IVYOM` | I VOTE YES ON ME       | `5d1b3f818c42a9621cc8348ab4ae89eace761b53ecb725b3ff62f56e` |
| 4 | `ORG`   | ORGANIC DISTRIBUTION   | `80f626b1d5ad7a53478d9aced308f570e2cf47746a1cdaaef4e8013b` |
| 5 | `HOTEL` | YOU CAN NEVER LEAVE    | `d91bc5bcfe52b93baea834cb754b7b835021676225ba235a82fb2d89` |
| 6 | `NDL`   | NO DOORS LEFT          | `64996c3bdad619660de1236b82547e8421abeb7029630389cb1f7361` |
| 7 | `DNPG`  | DO NOT PASS GO         | `3e499ba0420b657eda31c61622a17c3d53edc1db0f5225022c3a2b00` |
| 8 | `SMOKE` | DECENTRALIZED          | `9079019e845fe096bb3783b1ccfb0dc4f340ea1edeeb31c71d88a5cc` |

⚠️ Because the policies carry **no signature requirement**, anyone can mint any number of these —
and anyone can mint *other* assets under the same policy id — until the deadline passes. That is
inherent to a signature-free mint and it is stated plainly on the live page too. It is not fine
print; it is the honest description of what a bare timelock is.

## Piece nine — the gate

`oligarch-gate/validators/gate.ak` (Aiken, Plutus V3). Minting is allowed when:

- **at least one of the eight pieces appears among the transaction's SPENT inputs.** Any piece;
  duplicates count. *Spending* is what proves ownership, because an input requires the owner's
  signature. **Reference inputs are deliberately rejected** — referencing something needs no
  signature, so it would prove nothing.
- exactly one asset is minted, quantity exactly 1 — no batches, and **no burn, ever**;
- the asset name carries the `PFP` prefix, applied as a compile-time parameter via
  `aiken blueprint apply` (which is also what makes test policies genuinely different ids).

**There is no deadline and no supply cap, and that is deliberate.** Mint as many as you like,
forever. A set bought on the secondary market in ten years still mints.

**Live policy:** `534066fa3a4cc90aa9b01a0daa68a27fc5a98b466d1e519ff1cf82bd`

Verify the policy id three independent ways — `aiken` itself, `blake2b224(0x03 ‖ compiledCode)`, and
CSL's `PlutusScript.new_v3(compiledCode)`. Note that the other CSL constructors give a *wrong* hash
because `compiledCode` is already CBOR-wrapped.

### The catalogue

`build_pfp.py` is the reference builder: **9 backgrounds × 8 hats × 8 eyes × 10 mouths × 5 necks ×
7 marks × 5 pets = 1,008,000 combinations**, before the 32-character line you write yourself. The
backgrounds are motifs of the eight pieces, so the series appears inside its own sequel.

`build_pfp_page.py` embeds a JavaScript mirror of that builder which must produce **byte-identical
SVG** — what the page previews is exactly what goes on chain. `run_parity.py` is what enforces it.

## The wall

`build_wall.py` bakes every mint under the live policy into a static page, and the page also
**tops up live from the chain on every visit**, so a fresh mint appears without a redeploy.

## Layout

| path | what |
|---|---|
| `oligarch-gate/validators/gate.ak` | the Plutus V3 any-of-eight gate |
| `oligarch-gate/plutus.json` | compiled blueprint |
| `build_pfp.py` | reference SVG builder + trait catalogue |
| `build_pfp_page.py` | the maker page (embeds the JS mirror of the builder) |
| `build_gate_page.py` | the mint page |
| `build_wall.py` | the wall — bake + live top-up |
| `run_parity.py` | proves Python and JS builders agree byte for byte |
| `pfptest.mjs`, `gatetest.mjs`, `paritytest.mjs` | stub-wallet harnesses (incl. negative cases) |
| `evaluate.mjs`, `evaluate9.mjs` | build a real unsigned tx and have a node evaluate it |
| `RECEIPTS.json` | compiled hashes, ex-units, measured byte ceilings |

## Reproducing

```sh
cd oligarch-gate && aiken check && aiken build     # 9 tests: 1 positive, 8 negative
python3 run_parity.py                              # Python builder == JS mirror, byte for byte
node pfptest.mjs                                   # default / --nopure / --one / --none
```

`evaluate*.mjs` need a Blockfrost project id. Point `BLOCKFROST_PROJECT_ID_FILE` at a file
containing it, or drop it at `~/.blockfrost_project_id`. `TEST_ADDR` overrides the throwaway
address the harnesses build transactions against.

## Why this exists

If this repository disappeared, and the page disappeared with it, every picture would still be
recoverable from the Cardano chain, and so would the contract that governs the ninth — a Plutus
script ships in the witness set of the transaction that uses it. That is the entire point of
putting the art inside the transaction instead of behind a link.

## Licence

MIT. The artwork is satire.
