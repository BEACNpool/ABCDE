WITH names(drep_id,entity,group_name,has_script) AS (VALUES ('drep1g2d3y3skgr806wj2ryhhc5ca3akx6vmppde87jq7kgknjmv589e','Cardano Foundation','Cardano Foundation',true),('drep1m8mnpykcjfyax5mcs42whu3dt347u8aq43x45ucs6dv3ztw0lez','EMURGO','EMURGO',false),('drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt','Yoroi Wallet','EMURGO',false))
          SELECT n.drep_id,n.entity,n.group_name,h.id AS drep_hash_id,h.has_script,
            od.given_name,a.url AS identity_anchor_url
          FROM names n JOIN public.drep_hash h ON h.view=n.drep_id AND h.has_script=n.has_script
          LEFT JOIN LATERAL (SELECT r.voting_anchor_id FROM public.drep_registration r
            WHERE r.drep_hash_id=h.id AND r.voting_anchor_id IS NOT NULL
            ORDER BY r.tx_id DESC,r.cert_index DESC LIMIT 1) r ON true
          LEFT JOIN public.voting_anchor a ON a.id=r.voting_anchor_id
          LEFT JOIN public.off_chain_vote_data vd ON vd.voting_anchor_id=a.id
          LEFT JOIN public.off_chain_vote_drep_data od ON od.off_chain_vote_data_id=vd.id
          ORDER BY n.drep_id;
