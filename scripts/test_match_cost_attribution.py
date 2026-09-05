import copy
import unittest
from match_snapshot import (MINSWAP_ORDER_SCRIPT, MINSWAP_POOL_SCRIPT,
    USDM_POLICY, LIQWID_MARKET_BY_POLICY, minswap_fill_cost, find_pool,
    describe, cost_rollup, market_activity)

AGENT = {'id':'beacn', 'payment_cred':'owner', 'name':'BEACN'}
OTHER = {'id':'grokbot', 'payment_cred':'opponent', 'name':'grokbot'}

def node(cred, ada, usdm=0):
    return {'payment_addr':{'cred':cred, 'bech32':cred}, 'value':str(round(ada*1e6)),
            'asset_list':[{'policy_id':USDM_POLICY,'quantity':str(round(usdm*1e6))}]}

def order(receiver, usdm):
    n=node(MINSWAP_ORDER_SCRIPT,4,usdm)
    n['payment_addr']['bech32']='our-order' if receiver=='owner' else 'other-order'
    f=[{} for _ in range(9)]
    f[1]={'fields':[{'constructor':0,'fields':[{'bytes':receiver}]}]}
    f[7]={'int':2000000}
    n['inline_datum']={'value':{'constructor':0,'fields':f}}
    return n

def shared_batch():
    # The real failure shape: our 24 USDM exit alongside another 2,220 USDM.
    return {'inputs':[node(MINSWAP_POOL_SCRIPT,20000,1000), order('owner',24),
                      order('another',2220)],
            'outputs':[node(MINSWAP_POOL_SCRIPT,10060,3244),node('owner',108),
                       node('another',9836)], 'fee':'700000'}

class CostAttributionTest(unittest.TestCase):
    def test_shared_batch_does_not_charge_other_traders_to_us(self):
        tx=shared_batch()
        self.assertIsNone(find_pool(tx,-24))
        self.assertEqual(minswap_fill_cost(tx,AGENT,{'our-order'}),2)
        moves=[{'agent':'beacn','tx_hash':'fill','kind':'fill','fee':0,
                'ada_delta':104,'usdm_delta':-24}]
        costs=cost_rollup([AGENT],moves,{'fill':tx},{'beacn':['our-order']})['beacn']
        self.assertEqual(costs['service'],2)
        self.assertEqual(costs['ada_into_pool'],-106)
        self.assertEqual(costs['swaps'],1)
        kind,title,detail=describe(tx,AGENT,OTHER,{'our-order'},104,-24,False,0)
        self.assertEqual(kind,'fill')
        self.assertIn('USDM sold for 106.000000 ADA',detail)
        self.assertNotIn('landed',detail)

    def test_fee_cap_is_not_automatically_actual_fee(self):
        tx=shared_batch();tx['outputs'][1]['value']='109000000'
        with self.assertRaisesRegex(ValueError,'fees differ'):
            minswap_fill_cost(tx,AGENT,{'our-order'})

    def test_missing_datum_does_not_guess_fee(self):
        tx=shared_batch();tx['inputs'][1]['inline_datum']=None
        with self.assertRaisesRegex(ValueError,'fee datum'):
            minswap_fill_cost(tx,AGENT,{'our-order'})

    def test_wrong_receiver_fails(self):
        tx=shared_batch()
        tx['inputs'][1]['inline_datum']['value']['fields'][1]['fields'][0]['fields'][0]['bytes']='thief'
        with self.assertRaisesRegex(ValueError,'receiver differs'):
            minswap_fill_cost(tx,AGENT,{'our-order'})

    def test_supply_is_not_spot_trade_or_batcher_cost(self):
        policy=next(k for k,v in LIQWID_MARKET_BY_POLICY.items() if v=='USDM')
        q=node('owner',99.6);q['asset_list']=[{'policy_id':policy,'quantity':'3131243117'}]
        tx={'inputs':[node('owner',100,78.5)],'outputs':[q],'fee':'400000',
            'assets_minted':[{'policy_id':policy,'quantity':'3131243117'}]}
        kind,_,_=describe(tx,AGENT,OTHER,set(),-.4,-78.5,True,.4)
        self.assertEqual(kind,'supply')
        move={'agent':'beacn','tx_hash':'supply','kind':kind,'fee':.4,
              'ada_delta':-.4,'usdm_delta':-78.5}
        costs=cost_rollup([AGENT],[move],{'supply':tx},{'beacn':[]})['beacn']
        self.assertEqual(costs['service'],0)
        self.assertEqual(costs['total'],.4)
        self.assertEqual(market_activity('beacn',[move],78.5)['completed_trades'],0)
        transfer=copy.deepcopy(tx);transfer['assets_minted']=[]
        self.assertEqual(describe(transfer,AGENT,OTHER,set(),-.4,-78.5,True,.4)[0],'receipt')
        tx['inputs'],tx['outputs']=tx['outputs'],tx['inputs']
        tx['assets_minted'][0]['quantity']='-3131243117'
        self.assertEqual(describe(tx,AGENT,OTHER,set(),-.4,78.5,True,.4)[0],'redeem')

if __name__=='__main__':unittest.main()
