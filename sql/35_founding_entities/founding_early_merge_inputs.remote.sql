SELECT encode(t.hash,'hex') AS tx_hash,b.time AS block_time,
          encode(pt.hash,'hex') AS input_tx_hash,o.index AS input_index,o.value::bigint AS value_lovelace,o.address
          FROM public.tx t JOIN public.block b ON b.id=t.block_id JOIN public.tx_in i ON i.tx_in_id=t.id
          JOIN public.tx pt ON pt.id=i.tx_out_id JOIN public.tx_out o ON o.tx_id=i.tx_out_id AND o.index=i.tx_out_index
          WHERE t.hash=decode('c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76','hex') ORDER BY input_tx_hash,input_index;
