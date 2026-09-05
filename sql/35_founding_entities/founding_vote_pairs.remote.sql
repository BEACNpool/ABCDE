WITH latest AS (SELECT DISTINCT ON (v.drep_voter,v.gov_action_proposal_id)
        h.view AS drep_id,v.gov_action_proposal_id,v.vote
        FROM public.voting_procedure v JOIN public.drep_hash h ON h.id=v.drep_voter
        WHERE h.view IN ('drep1g2d3y3skgr806wj2ryhhc5ca3akx6vmppde87jq7kgknjmv589e','drep1m8mnpykcjfyax5mcs42whu3dt347u8aq43x45ucs6dv3ztw0lez','drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt') AND h.has_script=(h.view='drep1g2d3y3skgr806wj2ryhhc5ca3akx6vmppde87jq7kgknjmv589e') AND v.invalid IS NULL
        ORDER BY v.drep_voter,v.gov_action_proposal_id,v.tx_id DESC,v.index DESC)
          SELECT a.drep_id AS a,b.drep_id AS b,count(*) AS joint_actions,
            count(*) FILTER(WHERE a.vote=b.vote) AS same_votes,
            count(*) FILTER(WHERE (a.vote='Yes' AND b.vote='No') OR (a.vote='No' AND b.vote='Yes')) AS opposing_yes_no
          FROM latest a JOIN latest b ON a.gov_action_proposal_id=b.gov_action_proposal_id AND a.drep_id<b.drep_id
          GROUP BY a.drep_id,b.drep_id ORDER BY 1,2;
