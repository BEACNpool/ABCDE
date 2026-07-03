-- F11 receipt 8: magnitude profile of the top hop-1 enterprise hubs, keyed by
-- payment credential (enterprise addresses have no stake part; payment_cred
-- identifies them and uses idx_tx_out_payment_cred).
--
-- We report lifetime output count and gross received ADA only. A full
-- current-balance/pass-through aggregate is intentionally NOT run: these hubs
-- carry 1M+ outputs each and gross receipts far exceeding the ~45.6B ADA total
-- supply, so an unspent anti-join over them is unbounded and unnecessary — the
-- magnitude itself classifies them as recirculating settlement/hot addresses
-- (the same coins cycle through repeatedly), not accumulation sinks.
select
  encode(o.payment_cred, 'hex') as payment_cred_hex,
  count(*) as lifetime_outputs,
  round(sum(o.value)/1e6, 0) as gross_received_ada
from public.tx_out o
where o.payment_cred in (
  decode('6904e8b2c26f3dda6c4a5db4b3ec9e31d581c9960977cfe9c6917a43','hex'),
  decode('79e67550b2ff311da1883ad0ccc6fb2bb7c75e5489acff735fcc6878','hex'),
  decode('0237be10f5ec0ccb6cbd226b112f0940fed44ae0466d9b53962ba8b1','hex'),
  decode('d91ef01b73f3010bb173945cf5417257c00c002715a13052015ab54f','hex')
)
group by o.payment_cred
order by gross_received_ada desc;
