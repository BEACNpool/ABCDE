--
-- PostgreSQL database dump
--

\restrict 7rgWCnosSKe6ShW09KZOUTVBip90lcNAGI2HDc1xhok6E6OciydaJdFqzpvfvyL

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: byron_ddz_address_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.byron_ddz_address_stats (
    address character varying,
    tx_count bigint,
    total_received_lovelace numeric,
    total_received_ada numeric,
    first_epoch integer,
    last_epoch integer,
    epoch_span integer
);


--
-- Name: byron_ddz_counterparties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.byron_ddz_counterparties (
    target_address character varying,
    unique_source_addresses bigint
);


--
-- Name: byron_ddz_outputs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.byron_ddz_outputs (
    tx_out_id bigint,
    tx_id bigint,
    tx_out_index public.txindex,
    address character varying,
    value public.lovelace,
    epoch_no public.word31type,
    block_time timestamp without time zone
);


--
-- Name: derived_rewards_by_epoch; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.derived_rewards_by_epoch (
    epoch_no bigint NOT NULL,
    rewards_earned_lovelace numeric NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: labels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.labels (
    address text NOT NULL,
    label text,
    category text,
    confidence text,
    source text,
    pool_ticker text,
    pool_id text,
    role text
);


--
-- Name: probable_byron_exchanges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.probable_byron_exchanges (
    address character varying,
    tx_count bigint,
    unique_counterparties bigint,
    total_received_ada numeric,
    first_epoch integer,
    last_epoch integer,
    epoch_span integer,
    exchange_confidence text
);


--
-- Name: reverse_chain_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reverse_chain_results (
    entity text,
    depth integer,
    target_tx_hash text,
    target_epoch integer,
    src_addr text,
    src_value_ada numeric,
    src_tx_hash text,
    src_epoch integer,
    src_time timestamp with time zone,
    src_era text,
    src_stake_address text
);


--
-- Name: reverse_target_addrs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reverse_target_addrs (
    stake_address character varying,
    payment_address character varying,
    first_seen_epoch integer,
    first_seen_time timestamp without time zone
);


--
-- Name: reverse_trace_funding_sources; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reverse_trace_funding_sources (
    stake_address character varying,
    target_addr character varying,
    first_seen_epoch integer,
    source_tx_id bigint,
    source_address character varying,
    source_value public.lovelace,
    source_epoch public.word31type,
    source_time timestamp without time zone,
    source_era text
);


--
-- Name: traced_edges; Type: TABLE; Schema: public; Owner: -
--

CREATE UNLOGGED TABLE public.traced_edges (
    root_entity text,
    root_seed_address text,
    hop integer,
    src_tx_hash text,
    src_address text,
    src_value bigint,
    dest_tx_hash text,
    dest_address text,
    dest_value bigint,
    output_index integer,
    epoch_no integer,
    block_time timestamp with time zone,
    is_change_candidate boolean,
    is_shelley boolean,
    stake_address_id bigint,
    stake_address_view text
);


--
-- Name: traced_edges_deferred; Type: TABLE; Schema: public; Owner: -
--

CREATE UNLOGGED TABLE public.traced_edges_deferred (
    root_entity text,
    root_seed_address text,
    hop integer,
    src_tx_hash text,
    src_address text,
    src_value bigint,
    dest_tx_hash text,
    dest_address text,
    dest_value bigint,
    output_index integer,
    epoch_no integer,
    block_time timestamp with time zone,
    is_change_candidate boolean,
    is_shelley boolean,
    stake_address_id bigint,
    stake_address_view text
);


--
-- Name: derived_rewards_by_epoch derived_rewards_by_epoch_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.derived_rewards_by_epoch
    ADD CONSTRAINT derived_rewards_by_epoch_pkey PRIMARY KEY (epoch_no);


--
-- Name: labels labels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.labels
    ADD CONSTRAINT labels_pkey PRIMARY KEY (address);


--
-- Name: idx_byron_ddz_address; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_byron_ddz_address ON public.byron_ddz_outputs USING btree (address);


--
-- Name: idx_byron_ddz_txid; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_byron_ddz_txid ON public.byron_ddz_outputs USING btree (tx_id);


--
-- Name: idx_byron_stats_txcount; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_byron_stats_txcount ON public.byron_ddz_address_stats USING btree (tx_count DESC);


--
-- Name: idx_labels_address; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_labels_address ON public.labels USING btree (address);


--
-- Name: idx_labels_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_labels_category ON public.labels USING btree (category);


--
-- Name: idx_labels_trimmed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_labels_trimmed ON public.labels USING btree (TRIM(BOTH FROM address));


--
-- Name: idx_reverse_target_addr; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_reverse_target_addr ON public.reverse_target_addrs USING btree (payment_address);


--
-- Name: idx_reverse_target_stake; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_reverse_target_stake ON public.reverse_target_addrs USING btree (stake_address);


--
-- Name: idx_te_dest_addr; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_te_dest_addr ON public.traced_edges USING btree (dest_address);


--
-- Name: idx_te_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_te_entity ON public.traced_edges USING btree (root_entity);


--
-- Name: idx_te_hop; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_te_hop ON public.traced_edges USING btree (hop);


--
-- Name: idx_te_shelley; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_te_shelley ON public.traced_edges USING btree (is_shelley);


--
-- Name: idx_te_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_te_unique ON public.traced_edges USING btree (root_entity, hop, src_tx_hash, src_address, dest_tx_hash, dest_address, output_index);


--
-- Name: idx_ted_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_ted_unique ON public.traced_edges_deferred USING btree (root_entity, hop, src_tx_hash, src_address, dest_tx_hash, dest_address, output_index);


--
-- PostgreSQL database dump complete
--

\unrestrict 7rgWCnosSKe6ShW09KZOUTVBip90lcNAGI2HDc1xhok6E6OciydaJdFqzpvfvyL

