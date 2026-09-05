SELECT encode(t.hash,'hex') AS gov_action_tx_hash,g.index AS gov_action_index,
          g.type,b.time AS submitted_at,g.ratified_epoch,g.enacted_epoch,g.expired_epoch,g.dropped_epoch,
          a.url AS anchor_url,COALESCE(o.json->'body'->>'title',o.json->>'title') AS title,
          (SELECT sum(w.amount)::bigint FROM public.treasury_withdrawal w WHERE w.gov_action_proposal_id=g.id) AS requested_lovelace
          FROM public.gov_action_proposal g JOIN public.tx t ON t.id=g.tx_id JOIN public.block b ON b.id=t.block_id
          LEFT JOIN public.voting_anchor a ON a.id=g.voting_anchor_id
          LEFT JOIN public.off_chain_vote_data o ON o.voting_anchor_id=a.id
          ORDER BY g.tx_id,g.index;
