# BEACN brand assets

Canonical source on midnight: `~/projects/beacn-brand/`.

David supplied `BEACN-front-4K.png` and `BEACN-engraved-4K.glb` on 2026-09-04.
The unchanged originals live in `masters/`. `web/` contains deterministic resized
PNG/WebP icons and social images plus the optimized 3D model and its local decoder.
Use the master PNG for new image work and the master GLB for new Blender work.
Use the smaller derivatives on websites. Never load the 4K master model as a page icon.

- `web/pfp.png`: 1024-square PNG.
- `web/beacon-poster.webp`: 1024-square supplied front portrait.
- `web/icon-{16,32,48,64,180,192,256,512}.png`: platform sizes.
- `web/og.png`: 1200×630 preview, full badge contained without cropping.
- `web/beacn.glb`: 2K web model, original geometry retained; see media validation receipt.
- `web/draco/`: self-hosted decoder needed by the optimized web model.

Publish new presentation URLs with a version (`20260904`) and update service-worker
caches. Historical minted SVGs, immutable metadata, finished films and frozen bumpers
retain their original bytes. Product identities such as Ledger Scrolls remain intact;
the beacon identifies BEACN as their maintainer.

The pool site's existing `/pfp.png` is referenced by registered DRep metadata and is
preserved. New public branding uses `/pfp-20260904.png`. The existing live file already
differs from the registered image checksum; this refresh does not repair or change
that earlier discrepancy. Any registered metadata change is a separate on-chain task.

SHA-256 file receipts are in `SHA256SUMS`. Film tooling defaults and the website
rollout are recorded in workspace `infra/BEACN_BRANDING.md`.
