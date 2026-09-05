SELECT block_no,epoch_no,time,encode(hash,'hex') AS hash, current_timestamp AS observed_utc FROM public.block ORDER BY id DESC LIMIT 1;
