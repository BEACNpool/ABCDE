SELECT d.epoch_no,h.view AS drep_id,h.id AS drep_hash_id,h.has_script,d.amount AS amount_lovelace,d.active_until
          FROM public.drep_distr d JOIN public.drep_hash h ON h.id=d.hash_id
          WHERE d.epoch_no=(SELECT epoch_no FROM public.block ORDER BY id DESC LIMIT 1)
            OR (h.view IN ('drep1g2d3y3skgr806wj2ryhhc5ca3akx6vmppde87jq7kgknjmv589e','drep1m8mnpykcjfyax5mcs42whu3dt347u8aq43x45ucs6dv3ztw0lez','drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt') AND h.has_script=(h.view='drep1g2d3y3skgr806wj2ryhhc5ca3akx6vmppde87jq7kgknjmv589e') AND d.epoch_no>=630)
          ORDER BY d.epoch_no,h.view,h.has_script,h.id;
