-- Target public DuckDB schema for ABCDE Genesis forensic database.
-- This is a contract/schema note; generation happens through scripts/build_seed_artifacts.py until the full publisher exists.

CREATE SCHEMA IF NOT EXISTS genesis;
CREATE SCHEMA IF NOT EXISTS governance;
CREATE SCHEMA IF NOT EXISTS labels;
CREATE SCHEMA IF NOT EXISTS evidence;

-- Core source tables/views currently implemented in the seed cut:
-- genesis.seed_registry
-- genesis.seed_outputs
-- genesis.seed_first_spends
-- genesis.seed_first_spend_inputs
-- genesis.fourth_entry_direct_cospend
-- genesis.fourth_entry_sale_ticket_signal
-- genesis.bounded_trace_depth3

-- Planned governance tables:
-- governance.trace_stake_credentials
-- governance.stake_pool_delegations
-- governance.stake_pool_delegation_rollups
-- governance.stake_drep_delegations
-- governance.stake_drep_delegation_rollups
-- governance.known_pools
-- governance.known_dreps
