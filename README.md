# ABCDE — final archive (September 2026)

This branch is an orphan snapshot written when the ABCDE warehouse server was powered off and
BEACN retired as a stake pool (retirement effective epoch 656, 16 September 2026). Nothing here
needs a server. The code, findings and method docs stay on `main`, and the static explorer stays
on `gh-pages` at <https://beacnpool.github.io/ABCDE/>.

| Path | What it is |
|---|---|
| [`warehouse/`](warehouse/) | Final export of the derived schemas from `cexplorer_replica`: gzipped CSV, schema DDL, row counts and SHA-256 checksums. Read its README before using the data. |
| [`research/`](research/) | Loose query tooling and result files that lived only on the server: ADA Handle trace queries, the NIGHT full spend-flow export SQL, and the 318M-ADA reserve withdrawal trace TSVs. |
| [`brand/`](brand/) | The BEACN brand kit: masters, web derivatives and the 3D badge. |
| [`pool/`](pool/) | The pool's registered metadata JSON (exact bytes, hash-verified) and retirement receipts. |

Related archives:

- Pool website (formerly beacnpool.org): <https://beacnpool.github.io/ABCDE/pool/>, with source history on the `archive/beacnpool-site` branch.
- Films: <https://beacnpool.github.io/ABCDE/films/> and <https://beacnpool.github.io/ledger-scrolls/films/>.
- DRep voting archive: <https://beacnpool.github.io/beacn-drep-web/>.
