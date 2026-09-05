SELECT encode(t.hash,'hex') AS tx_hash,r.cert_index,sa.view AS stake_address,
          r.amount::bigint AS value_lovelace,b.epoch_no,b.time AS block_time FROM public.reserve r
          JOIN public.stake_address sa ON sa.id=r.addr_id JOIN public.tx t ON t.id=r.tx_id
          JOIN public.block b ON b.id=t.block_id WHERE t.hash=decode('03b02cff29a5f2dfc827e00345eaab8b29a3d740e9878aa6e5dd2b52da0763c5','hex') ORDER BY r.cert_index,sa.view;
