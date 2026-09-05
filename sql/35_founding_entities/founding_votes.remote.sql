SELECT h.view AS drep_id,h.id AS drep_hash_id,h.has_script,encode(gt.hash,'hex') AS gov_action_tx_hash,
          g.index AS gov_action_index,g.type AS gov_action_type,v.vote,
          encode(t.hash,'hex') AS ballot_tx_hash,v.tx_id AS ballot_tx_id,v.index AS ballot_index,
          b.block_no,b.time AS block_time,v.invalid,a.url AS rationale_url
          FROM public.voting_procedure v JOIN public.drep_hash h ON h.id=v.drep_voter
          JOIN public.gov_action_proposal g ON g.id=v.gov_action_proposal_id
          JOIN public.tx gt ON gt.id=g.tx_id JOIN public.tx t ON t.id=v.tx_id
          JOIN public.block b ON b.id=t.block_id LEFT JOIN public.voting_anchor a ON a.id=v.voting_anchor_id
          WHERE h.view IN ('drep1g2d3y3skgr806wj2ryhhc5ca3akx6vmppde87jq7kgknjmv589e','drep1m8mnpykcjfyax5mcs42whu3dt347u8aq43x45ucs6dv3ztw0lez','drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt') AND h.has_script=(h.view='drep1g2d3y3skgr806wj2ryhhc5ca3akx6vmppde87jq7kgknjmv589e') ORDER BY v.tx_id,v.index,h.view;
