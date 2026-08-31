/* MINFREE — minPoolCost model.
   Protocol constants from Koios epoch 650 (last complete epoch with rewards)
   plus epoch 652 tip for the live floor. Pledge influence (a0) is omitted on
   purpose: it changes the shape of well-pledged pools, not the flat floor.
*/
(function (root) {
  "use strict";

  const ADA_PER_BLOCK = 293.38;          // epoch 650 avg_blk_reward
  const ACTIVE_STAKE = 21511857227.960853; // epoch 650 active_stake, ADA
  const K = 500;
  const SLOTS = 21600;
  const EPOCHS_YEAR = 73;                // 365 / 5
  const SATURATION = ACTIVE_STAKE / K;   // ~43.02M ADA
  const CURRENT_FLOOR = 170;
  const PROPOSED_FLOOR = 75;
  const OLD_FLOOR = 340;
  const SMALL_STAKE = 1000000; // featured comparison: a ~1M ₳ independent, not a dust pool

  const SAMPLES = [
    {
      id: "hive", ticker: "HIVE", label: "Hobby · 1.4M",
      blurb: "1.41M ₳, 1% margin, sitting on the 170 floor. About one block an epoch.",
      stake: 1410303, pledge: 10000, margin: 0.01, declared: 170,
    },
    {
      id: "bio", ticker: "BIO", label: "Hobby · 1.4M · 340",
      blurb: "1.41M ₳, 3% margin, declared 340. Race-off, the floor drop does not move them.",
      stake: 1414300, pledge: 1000, margin: 0.03, declared: 340,
    },
    {
      id: "frog2", ticker: "FROG2", label: "Community · 5.8M",
      blurb: "5.84M ₳, 4% margin, declared cost still 340.",
      stake: 5837544, pledge: 150000, margin: 0.04, declared: 340,
    },
    {
      id: "cflow", ticker: "CFLOW", label: "Mid · 16M",
      blurb: "16.0M ₳, 1.9% margin, declared 340.",
      stake: 15980109, pledge: 100000, margin: 0.019, declared: 340,
    },
    {
      id: "sipo", ticker: "SIPO", label: "Near saturate · 42M",
      blurb: "42.2M ₳, 3.9% margin, declared 340. One more percent and it is full.",
      stake: 42154687, pledge: 50000, margin: 0.039, declared: 340,
    },
    {
      id: "atada", ticker: "ATADA", label: "Over-sat · 65M",
      blurb: "65.4M ₳ on a 43M cap. Extra stake mints nothing. 340 cost is a rounding error.",
      stake: 65368957, pledge: 1300000, margin: 0.01, declared: 340,
    },
  ];

  function poissonPmf(lambda, n) {
    if (lambda === 0) return n === 0 ? 1 : 0;
    let p = Math.exp(-lambda);
    for (let i = 1; i <= n; i++) p *= lambda / i;
    return p;
  }

  function splitEpoch(gross, cost, margin) {
    if (gross <= 0) {
      return { gross: 0, opFixed: 0, opMargin: 0, delPot: 0 };
    }
    if (gross <= cost) {
      return { gross, opFixed: gross, opMargin: 0, delPot: 0 };
    }
    const rem = gross - cost;
    const opMargin = rem * margin;
    return { gross, opFixed: cost, opMargin, delPot: rem - opMargin };
  }

  function expected(stake, pledge, margin, declared, floor) {
    const apparent = Math.min(Math.max(0, stake), SATURATION);
    const lambda = SLOTS * apparent / ACTIVE_STAKE;
    const cost = Math.max(floor, declared);
    const cap = Math.max(24, Math.ceil(lambda + 8 * Math.sqrt(lambda + 1)) + 4);
    let opFixed = 0, opMargin = 0, delPot = 0, gross = 0, pMass = 0;
    for (let n = 0; n <= cap; n++) {
      const p = poissonPmf(lambda, n);
      pMass += p;
      const s = splitEpoch(n * ADA_PER_BLOCK, cost, margin);
      opFixed += p * s.opFixed;
      opMargin += p * s.opMargin;
      delPot += p * s.delPot;
      gross += p * s.gross;
    }
    // leftover tail (should be ~0) treated as the mean of the truncated Poisson
    if (pMass < 0.999 && lambda > 0) {
      const s = splitEpoch(lambda * ADA_PER_BLOCK, cost, margin);
      const w = 1 - pMass;
      opFixed += w * s.opFixed;
      opMargin += w * s.opMargin;
      delPot += w * s.delPot;
      gross += w * s.gross;
    }
    const pldg = Math.min(Math.max(0, pledge), Math.max(0, stake));
    const opPledge = stake > 0 ? delPot * (pldg / stake) : 0;
    const roa = stake > 0 ? (delPot / stake) * EPOCHS_YEAR : 0;
    const lucky = splitEpoch(ADA_PER_BLOCK, cost, margin);
    return {
      lambda, cost, gross, opFixed, opMargin, delPot, opPledge,
      opTotal: opFixed + opMargin + opPledge,
      roa,
      lucky,
      apparent,
      saturated: stake > SATURATION + 1,
    };
  }

  function costFor(pool, floor, race) {
    return race ? floor : Math.max(floor, pool.declared);
  }

  function fmtAda(n, digits) {
    const d = digits == null ? (Math.abs(n) >= 100 ? 0 : 2) : digits;
    if (!isFinite(n)) return "—";
    const abs = Math.abs(n);
    const sign = n < 0 ? "−" : "";
    if (abs >= 1e9) return sign + (abs / 1e9).toFixed(2) + "B ₳";
    if (abs >= 1e6) return sign + (abs / 1e6).toFixed(2) + "M ₳";
    if (abs >= 10000) return sign + Math.round(abs).toLocaleString("en-US") + " ₳";
    if (abs >= 100) return sign + abs.toFixed(d) + " ₳";
    return sign + abs.toFixed(d) + " ₳";
  }

  function fmtPct(x, digits) {
    const d = digits == null ? 2 : digits;
    if (!isFinite(x)) return "—";
    return (x * 100).toFixed(d) + "%";
  }

  function fmtX(x) {
    if (!isFinite(x) || x > 999) return "∞";
    if (x >= 10) return x.toFixed(1) + "×";
    return x.toFixed(2) + "×";
  }

  function fmtBlk(l) {
    if (!isFinite(l)) return "—";
    if (l < 1) return l.toFixed(3);
    if (l < 10) return l.toFixed(2);
    return l.toFixed(1);
  }

  const api = {
    ADA_PER_BLOCK, ACTIVE_STAKE, K, SLOTS, EPOCHS_YEAR, SATURATION,
    CURRENT_FLOOR, PROPOSED_FLOOR, OLD_FLOOR, SMALL_STAKE, SAMPLES,
    expected, splitEpoch, costFor, fmtAda, fmtPct, fmtX, fmtBlk,
  };
  root.MINFREE = api;
  if (typeof module !== "undefined") module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
