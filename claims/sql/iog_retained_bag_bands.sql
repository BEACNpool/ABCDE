SELECT
  band,
  round(ada, 6) AS ada,
  confidence,
  interpretation
FROM iog_current_bag_depth14_confidence_bands
ORDER BY
  CASE band
    WHEN 'trace_membership_current_upper_bound' THEN 1
    WHEN 'probable_retained_like_abstain_surface' THEN 2
    WHEN 'high_confidence_coordinated_retained_like_core' THEN 3
    WHEN 'no_latest_drep_surface' THEN 4
    WHEN 'live_iog_pool_stake_sanity_check' THEN 5
    ELSE 99
  END,
  band;
