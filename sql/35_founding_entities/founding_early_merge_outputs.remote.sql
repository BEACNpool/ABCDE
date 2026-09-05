SELECT encode(t.hash,'hex') AS tx_hash,o.index AS output_index,
          o.value::bigint AS value_lovelace,o.address,t.fee::bigint AS fee_lovelace
          FROM public.tx t JOIN public.tx_out o ON o.tx_id=t.id WHERE t.hash=decode('c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76','hex') ORDER BY o.index;
