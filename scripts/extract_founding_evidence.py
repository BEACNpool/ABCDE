#!/usr/bin/env python3
"""Extract a bounded public evidence cut from db-sync in one read-only snapshot.

Requires psql and an operator-supplied database/optional SSH target. Does not
change warehouse tables or call the public DuckDB query interface. --seal-only
refreshes the local manifest after editing the public-source register.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SMALL = ROOT / 'data/small'
SQL_DIR = ROOT / 'sql/35_founding_entities'
MANIFEST = ROOT / 'data/manifests/founding-evidence-manifest.json'
RECEIPTS = SMALL / 'founding_query_receipts.csv'
IDENTITIES = [
    ('drep1g2d3y3skgr806wj2ryhhc5ca3akx6vmppde87jq7kgknjmv589e', 'Cardano Foundation', 'Cardano Foundation'),
    ('drep1m8mnpykcjfyax5mcs42whu3dt347u8aq43x45ucs6dv3ztw0lez', 'EMURGO', 'EMURGO'),
    ('drep1qe2l8gw8v7ydswfp9twytxcc3wzwdq8npt55f3vnlgv2u8sx3nt', 'Yoroi Wallet', 'EMURGO'),
]
MERGE = 'c8596b9cd81f734f8129604ff86f23bd4a910465acb84ad9e9d1ac223ccb4a76'
RESERVE = '03b02cff29a5f2dfc827e00345eaab8b29a3d740e9878aa6e5dd2b52da0763c5'
BACKUP = None


def save(path: Path, content: str) -> None:
    global BACKUP
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() == content:
        return
    if path.exists():
        if BACKUP is None:
            BACKUP = Path(tempfile.mkdtemp(prefix='abcde-founding-backup-'))
        dest = BACKUP / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    path.write_text(content, encoding='utf-8')


def read_rows(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_text(rows: list[dict], fields: list[str] | None = None) -> str:
    if not rows and not fields:
        raise ValueError('No rows and no explicit field names')
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=fields or list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def queries() -> dict[str, str]:
    ids = ','.join("'" + x[0] + "'" for x in IDENTITIES)
    identity_values = ','.join('(' + ','.join("'"+v+"'" for v in row) + ',' + ('true' if row[1]=='Cardano Foundation' else 'false') + ')' for row in IDENTITIES)
    typed_filter = f"h.view IN ({ids}) AND h.has_script=(h.view='{IDENTITIES[0][0]}')"
    cohort = read_rows(SMALL / 'founding_cohort_keys.csv')
    if len(cohort) != 14 or len({r['stake_address'] for r in cohort}) != 14:
        raise ValueError('Expected the documented fourteen-credential selection')
    for row in cohort:
        if not row['stake_address'].startswith('stake1') or not row['stake_address'].isalnum():
            raise ValueError('Invalid cohort credential')
    keys = ','.join("'"+r['stake_address']+"'" for r in cohort)
    filtered_votes = f"""SELECT DISTINCT ON (v.drep_voter,v.gov_action_proposal_id)
        h.view AS drep_id,v.gov_action_proposal_id,v.vote
        FROM public.voting_procedure v JOIN public.drep_hash h ON h.id=v.drep_voter
        WHERE {typed_filter} AND v.invalid IS NULL
        ORDER BY v.drep_voter,v.gov_action_proposal_id,v.tx_id DESC,v.index DESC"""
    return {
        'founding_chain_tip': "SELECT block_no,epoch_no,time,encode(hash,'hex') AS hash, current_timestamp AS observed_utc FROM public.block ORDER BY id DESC LIMIT 1",
        'founding_drep_identity': f"""WITH names(drep_id,entity,group_name,has_script) AS (VALUES {identity_values})
          SELECT n.drep_id,n.entity,n.group_name,h.id AS drep_hash_id,h.has_script,
            od.given_name,a.url AS identity_anchor_url
          FROM names n JOIN public.drep_hash h ON h.view=n.drep_id AND h.has_script=n.has_script
          LEFT JOIN LATERAL (SELECT r.voting_anchor_id FROM public.drep_registration r
            WHERE r.drep_hash_id=h.id AND r.voting_anchor_id IS NOT NULL
            ORDER BY r.tx_id DESC,r.cert_index DESC LIMIT 1) r ON true
          LEFT JOIN public.voting_anchor a ON a.id=r.voting_anchor_id
          LEFT JOIN public.off_chain_vote_data vd ON vd.voting_anchor_id=a.id
          LEFT JOIN public.off_chain_vote_drep_data od ON od.off_chain_vote_data_id=vd.id
          ORDER BY n.drep_id""",
        'founding_drep_distribution': f"""SELECT d.epoch_no,h.view AS drep_id,h.id AS drep_hash_id,h.has_script,d.amount AS amount_lovelace,d.active_until
          FROM public.drep_distr d JOIN public.drep_hash h ON h.id=d.hash_id
          WHERE d.epoch_no=(SELECT epoch_no FROM public.block ORDER BY id DESC LIMIT 1)
            OR ({typed_filter} AND d.epoch_no>=630)
          ORDER BY d.epoch_no,h.view,h.has_script,h.id""",
        'founding_votes': f"""SELECT h.view AS drep_id,h.id AS drep_hash_id,h.has_script,encode(gt.hash,'hex') AS gov_action_tx_hash,
          g.index AS gov_action_index,g.type AS gov_action_type,v.vote,
          encode(t.hash,'hex') AS ballot_tx_hash,v.tx_id AS ballot_tx_id,v.index AS ballot_index,
          b.block_no,b.time AS block_time,v.invalid,a.url AS rationale_url
          FROM public.voting_procedure v JOIN public.drep_hash h ON h.id=v.drep_voter
          JOIN public.gov_action_proposal g ON g.id=v.gov_action_proposal_id
          JOIN public.tx gt ON gt.id=g.tx_id JOIN public.tx t ON t.id=v.tx_id
          JOIN public.block b ON b.id=t.block_id LEFT JOIN public.voting_anchor a ON a.id=v.voting_anchor_id
          WHERE {typed_filter} ORDER BY v.tx_id,v.index,h.view""",
        'founding_vote_pairs': f"""WITH latest AS ({filtered_votes})
          SELECT a.drep_id AS a,b.drep_id AS b,count(*) AS joint_actions,
            count(*) FILTER(WHERE a.vote=b.vote) AS same_votes,
            count(*) FILTER(WHERE (a.vote='Yes' AND b.vote='No') OR (a.vote='No' AND b.vote='Yes')) AS opposing_yes_no
          FROM latest a JOIN latest b ON a.gov_action_proposal_id=b.gov_action_proposal_id AND a.drep_id<b.drep_id
          GROUP BY a.drep_id,b.drep_id ORDER BY 1,2""",
        'founding_proposals': """SELECT encode(t.hash,'hex') AS gov_action_tx_hash,g.index AS gov_action_index,
          g.type,b.time AS submitted_at,g.ratified_epoch,g.enacted_epoch,g.expired_epoch,g.dropped_epoch,
          a.url AS anchor_url,COALESCE(o.json->'body'->>'title',o.json->>'title') AS title,
          (SELECT sum(w.amount)::bigint FROM public.treasury_withdrawal w WHERE w.gov_action_proposal_id=g.id) AS requested_lovelace
          FROM public.gov_action_proposal g JOIN public.tx t ON t.id=g.tx_id JOIN public.block b ON b.id=t.block_id
          LEFT JOIN public.voting_anchor a ON a.id=g.voting_anchor_id
          LEFT JOIN public.off_chain_vote_data o ON o.voting_anchor_id=a.id
          ORDER BY g.tx_id,g.index""",
        'founding_epoch_parameters': "SELECT epoch_no,dvt_treasury_withdrawal AS treasury_threshold,dvt_update_to_constitution AS constitution_threshold,dvt_committee_normal AS committee_threshold,protocol_major FROM public.epoch_param ORDER BY epoch_no DESC LIMIT 1",
        'founding_cohort_stake': f"""WITH wanted AS (SELECT id,view FROM public.stake_address WHERE view IN ({keys}))
          SELECT w.view AS stake_address,s.epoch_no,s.amount AS amount_lovelace,p.view AS pool_id,
            dh.view AS drep_id,b.time AS drep_cert_time,encode(t.hash,'hex') AS drep_cert_tx
          FROM wanted w LEFT JOIN public.epoch_stake s ON s.addr_id=w.id
            AND s.epoch_no=(SELECT epoch_no FROM public.block ORDER BY id DESC LIMIT 1)
          LEFT JOIN public.pool_hash p ON p.id=s.pool_id
          LEFT JOIN LATERAL (SELECT d.* FROM public.delegation_vote d WHERE d.addr_id=w.id
            ORDER BY tx_id DESC,cert_index DESC LIMIT 1) d ON true
          LEFT JOIN public.drep_hash dh ON dh.id=d.drep_hash_id
          LEFT JOIN public.tx t ON t.id=d.tx_id LEFT JOIN public.block b ON b.id=t.block_id ORDER BY w.view""",
        'founding_early_merge_inputs': f"""SELECT encode(t.hash,'hex') AS tx_hash,b.time AS block_time,
          encode(pt.hash,'hex') AS input_tx_hash,o.index AS input_index,o.value::bigint AS value_lovelace,o.address
          FROM public.tx t JOIN public.block b ON b.id=t.block_id JOIN public.tx_in i ON i.tx_in_id=t.id
          JOIN public.tx pt ON pt.id=i.tx_out_id JOIN public.tx_out o ON o.tx_id=i.tx_out_id AND o.index=i.tx_out_index
          WHERE t.hash=decode('{MERGE}','hex') ORDER BY input_tx_hash,input_index""",
        'founding_early_merge_outputs': f"""SELECT encode(t.hash,'hex') AS tx_hash,o.index AS output_index,
          o.value::bigint AS value_lovelace,o.address,t.fee::bigint AS fee_lovelace
          FROM public.tx t JOIN public.tx_out o ON o.tx_id=t.id WHERE t.hash=decode('{MERGE}','hex') ORDER BY o.index""",
        'founding_reserve_credits': f"""SELECT encode(t.hash,'hex') AS tx_hash,r.cert_index,sa.view AS stake_address,
          r.amount::bigint AS value_lovelace,b.epoch_no,b.time AS block_time FROM public.reserve r
          JOIN public.stake_address sa ON sa.id=r.addr_id JOIN public.tx t ON t.id=r.tx_id
          JOIN public.block b ON b.id=t.block_id WHERE t.hash=decode('{RESERVE}','hex') ORDER BY r.cert_index,sa.view""",
    }


def seal() -> None:
    receipts = read_rows(RECEIPTS)
    receipts = [r for r in receipts if r['source_kind'] not in ('public_sources', 'historical_selection')]
    fields = list(receipts[0])
    for name, kind in [('founding_public_sources', 'public_sources'), ('founding_cohort_keys', 'historical_selection')]:
        path = SMALL / (name+'.csv')
        if not path.exists():
            raise ValueError('Missing '+str(path.relative_to(ROOT)))
        rows = read_rows(path)
        dates = sorted(r['accessed_utc'] for r in rows) if kind == 'public_sources' else sorted(r['selection_snapshot_utc'] for r in rows)
        row = dict.fromkeys(fields, '')
        row.update(table_name=name,source_kind=kind,collection_started_utc=dates[0],collection_finished_utc=dates[-1],row_count=len(rows),csv_sha256=digest(path))
        receipts.append(row)
    save(RECEIPTS,csv_text(sorted(receipts,key=lambda r:r['table_name']),fields))
    tip = read_rows(SMALL/'founding_chain_tip.csv')[0]
    files = []
    for path in sorted(SMALL.glob('founding_*.csv')):
        files.append(dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=digest(path),row_count=len(read_rows(path))))
    for path in sorted(SQL_DIR.glob('*.remote.sql')):
        files.append(dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=digest(path)))
    dist = read_rows(SMALL/'founding_drep_distribution.csv')
    named = {r['drep_hash_id'] for r in read_rows(SMALL/'founding_drep_identity.csv')}
    pairs = [{k:(int(v) if k not in ('a','b') else v) for k,v in r.items()} for r in read_rows(SMALL/'founding_vote_pairs.csv')]
    payload = dict(schema_version=1,boundary_kind='repeatable_read_snapshot',
        chain_tip=dict(block_no=int(tip['block_no']),epoch_no=int(tip['epoch_no']),time=tip['time'],hash=tip['hash']),
        collection_scope='One read-only PostgreSQL snapshot for chain tables; public disclosures and historical cohort selection carry separate receipts.',
        files=files,expected_claims=dict(vote_pairs=pairs,
            latest_voting_power_by_drep={r['drep_id']:int(r['amount_lovelace']) for r in dist if r['epoch_no']==tip['epoch_no'] and r['drep_hash_id'] in named},
            early_merge_transaction_hash=MERGE,
            reserve_credit_lovelace=sum(int(r['value_lovelace']) for r in read_rows(SMALL/'founding_reserve_credits.csv'))))
    save(MANIFEST,json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
    print(f'Sealed {len(files)} public CSV/SQL files at block {tip["block_no"]}, epoch {tip["epoch_no"]}.')


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',help='db-sync database name, explicitly selected by the operator')
    parser.add_argument('--ssh-target',help='Optional SSH target; invokes sudo -u postgres psql remotely')
    parser.add_argument('--seal-only',action='store_true')
    args=parser.parse_args()
    if args.seal_only:
        seal(); return
    if not args.database:
        parser.error('--database is required for extraction')
    qs=queries()
    for name,sql in qs.items():
        save(SQL_DIR/(name+'.remote.sql'),sql.strip()+';\n')
    start=datetime.now(timezone.utc).isoformat()
    commands=["BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;", "SET LOCAL statement_timeout='45s';", "SET LOCAL lock_timeout='2s';", "SET LOCAL work_mem='16MB';", "SET LOCAL max_parallel_workers_per_gather=0;", "SET LOCAL timezone='UTC';"]
    for name,sql in qs.items():
        commands.append("SELECT json_build_object('table','"+name+"','rows',coalesce(json_agg(row_to_json(q)),'[]'::json)) FROM ("+sql+") q;")
    commands.append('COMMIT;')
    psql=['psql','-X','-q','-t','-A','-v','ON_ERROR_STOP=1','--dbname',args.database]
    cmd=['ssh',args.ssh_target,shlex.join(['sudo','-u','postgres',*psql])] if args.ssh_target else psql
    result=subprocess.run(cmd,input='\n'.join(commands),text=True,capture_output=True,timeout=180)
    if result.returncode:
        raise SystemExit('Read-only extraction failed: '+result.stderr)
    finish=datetime.now(timezone.utc).isoformat()
    results={entry['table']:entry['rows'] for entry in (json.loads(line) for line in result.stdout.splitlines() if line.strip())}
    if set(results)!=set(qs) or any(not rows for rows in results.values()):
        raise SystemExit('Incomplete extraction; no CSVs replaced')
    tip=results['founding_chain_tip'][0]
    receipts=[]
    for name,rows in results.items():
        path=SMALL/(name+'.csv')
        save(path,csv_text(rows))
        receipts.append(dict(table_name=name,source_kind='dbsync_atomic_snapshot',collection_started_utc=start,collection_finished_utc=finish,
            db_tip_block=tip['block_no'],db_tip_epoch=tip['epoch_no'],db_tip_time=tip['time'],db_tip_hash=tip['hash'],
            query_path=(SQL_DIR/(name+'.remote.sql')).relative_to(ROOT).as_posix(),row_count=len(rows),csv_sha256=digest(path)))
        print(f'{name}: {len(rows)} rows')
    save(RECEIPTS,csv_text(receipts))
    seal()


if __name__=='__main__':
    main()
