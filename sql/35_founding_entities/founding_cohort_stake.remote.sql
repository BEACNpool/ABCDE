WITH wanted AS (SELECT id,view FROM public.stake_address WHERE view IN ('stake1u84u9k7yjnujla4stf25q23r0tcxyj0stmzadwam4k98g3s0euwyc','stake1u88zeazj5xy8uamz47rqswpjvn9zmsyg78ahklfmku2k35g2qlaaj','stake1u8yr90g09a2znm4ylaspctgyteuslnrfn6flnntxkka2ysgy2750z','stake1u90k27vvycsnksgwrslmqryqyweh79r3zcp5hh2t92n65mgkqezp5','stake1u970ch6knl4j2wl4whfkrfdv5uj9u2uwemtnzdfhhzvv7ag7tcnr4','stake1u9j7tecyajslj3lk9pmnrd9456fpfdsnqufpd6vmnwqzg2qkzjl27','stake1u9ku4ja8eeens3hxmq26f53v6ujlymz6apyyfhm9g5rpvvqtur40t','stake1u9q6nedpj7kt7pm9sxgtu4sq37jgxk0lyfvs4wvdvz0tm2czk759g','stake1u9xs3xep7gyjxpxrfv0el7xm2gctntk88ax789zcrlwue3c2xzevu','stake1ux47d7aa3l8vk2pf0v6jlj39t00y7lagf68pewgw2cxkcasfmqr5h','stake1uxasl8h59m07npqm2fvf7jnfh4etfpufxnpr3d7wzx2nuzqfvwhyv','stake1uyclu4dwn93kvnn786x35efaj5nnfa05dd6w92fjgn6nwxcdg7hpg','stake1uylhqtxx5ng4tawhcs9n7jgls0mm3q7ely5r565mdz2upqqw8f05q','stake1uyv7u4rpvcv5vpv03ugf6rr8ydt3qyjy682xfkzs4snyqss7zayjf'))
          SELECT w.view AS stake_address,s.epoch_no,s.amount AS amount_lovelace,p.view AS pool_id,
            dh.view AS drep_id,b.time AS drep_cert_time,encode(t.hash,'hex') AS drep_cert_tx
          FROM wanted w LEFT JOIN public.epoch_stake s ON s.addr_id=w.id
            AND s.epoch_no=(SELECT epoch_no FROM public.block ORDER BY id DESC LIMIT 1)
          LEFT JOIN public.pool_hash p ON p.id=s.pool_id
          LEFT JOIN LATERAL (SELECT d.* FROM public.delegation_vote d WHERE d.addr_id=w.id
            ORDER BY tx_id DESC,cert_index DESC LIMIT 1) d ON true
          LEFT JOIN public.drep_hash dh ON dh.id=d.drep_hash_id
          LEFT JOIN public.tx t ON t.id=d.tx_id LEFT JOIN public.block b ON b.id=t.block_id ORDER BY w.view;
