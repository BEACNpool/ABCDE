-- genesis_tag_intersection.sql — cross the genesis reachability graph against
-- governance.genesis_address_tags. Read-only; run on abcde or via the API.
-- Confidence labels come from the tags table (FACT / STRONG_INFERENCE / UNKNOWN);
-- reachability is NOT value attribution — see tracers/README.md wording rule.

-- Genesis-reachable value landing at tagged addresses, grouped by tag.
SELECT t.tag, t.confidence,
       count(DISTINCT g.address)              AS addrs_hit,
       min(g.depth)                           AS min_depth,
       round(sum(g.value)/1e6)                AS ada_ever_received,
       round(sum(g.value) FILTER (WHERE g.spent_by_tx_id IS NULL)/1e6) AS ada_unspent_now
FROM governance.genesis_address_tags t
JOIN trace.genesis_reach g ON g.address = t.address
GROUP BY t.tag, t.confidence
ORDER BY ada_ever_received DESC NULLS LAST;

-- The genesis outputs that have never moved (depth 0, still unspent at tip).
SELECT count(*) AS outputs, round(sum(value)/1e6) AS total_ada
FROM trace.genesis_reach WHERE depth = 0 AND spent_by_tx_id IS NULL;
