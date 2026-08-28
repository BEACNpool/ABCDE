# web/cards — hand-authored social images

These are published to `gh-pages` under `/og/` by `web/publish_gh_pages.sh`.

They live here rather than in `web/dist/og/` because `scripts/build_og_cards.py`
**empties that directory before regenerating it** (`for f in p.iterdir(): f.unlink()`).
Anything hand-placed there is destroyed on the next build — which is exactly what
happened on 2026-08-27: a card was copied in, the publish script regenerated the
generated cards as its first step, and the hand-made one was gone before the copy
step ran. The deployed page then pointed at a 404.

They are committed rather than gitignored on purpose. The gitignored `media/`,
`og/` and `r/` directories were never deployed at all and 404'd for 34 days;
an asset a public URL points at should not depend on one machine's untracked files.
