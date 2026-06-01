SELECT
  band,
  round(ada, 6) AS ada,
  confidence,
  interpretation
FROM iog_current_bag_depth14_confidence_bands
ORDER BY ada DESC, band;
