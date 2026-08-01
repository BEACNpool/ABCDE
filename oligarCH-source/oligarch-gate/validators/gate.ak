//// oligarCH piece 9 — the PFP creator's minting policy. The final piece of the collection.
////
//// The ninth piece is not one picture: it is EVERY custom oligarCH, minted by the holders.
//// Minting requires spending AT LEAST ONE of the eight earlier pieces — any of them, it does
//// not matter which (David, 2026-07-31: "all owners are eligible"). Control is proved by
//// SPENDING: an input can only be spent with its owner's signature, so one piece among the
//// inputs is proof of ownership. The wallet returns the piece as change automatically.
////
//// ⚠️ REFERENCE INPUTS ARE DELIBERATELY NOT ACCEPTED. Referencing a UTxO requires no
//// signature, so anybody could reference a stranger's wallet and mint. `self.inputs` only.
////
//// ⚠️ NO DEADLINE AND NO SUPPLY CAP, both by design: "you can mint as many of the 9th NFT
//// forever because this policy will never die." A set traded on the secondary market in ten
//// years still mints. The page is a convenience — it is open source, and if it ever goes
//// away anyone can clone it (or hand-build the transaction) and keep minting. The POLICY is
//// the artifact, not the website.
////
//// ⚠️ THE POLICY ID IS THIS SCRIPT'S HASH. Editing anything below — including the eight
//// constants — produces a different policy id, i.e. a different collection. The earlier
//// all-eight variants (real `2927f7dd…`, test `7d6702e0…`) are superseded by this any-of
//// design and their mints stay where they are; this file is frozen once announced.

use aiken/collection/dict
use aiken/collection/list
use aiken/primitive/bytearray
use cardano/address.{Address, VerificationKey}
use cardano/assets.{PolicyId, Value}
use cardano/transaction.{
  Input, NoDatum, Output, OutputReference, Transaction, placeholder,
}

/// The eight earlier pieces, in release order. Each is the blake2b-224 hash of its own bare
/// timelock script, taken from `pieces.py` on 2026-07-30 — derived there, never hand-typed.
///   1 BYTTG  2 TGM  3 IVYOM  4 ORG  5 HOTEL  6 NDL  7 DNPG  8 SMOKE
const required: List<PolicyId> =
  [
    #"2ef849a4e7742f0705f41c7b2195bb828b934ee48dcfa0c204ae2a8d",
    #"7ba4e6b009013f83cae317390fd88c1b734154cc110ab1b31fbc4ac5",
    #"5d1b3f818c42a9621cc8348ab4ae89eace761b53ecb725b3ff62f56e",
    #"80f626b1d5ad7a53478d9aced308f570e2cf47746a1cdaaef4e8013b",
    #"d91bc5bcfe52b93baea834cb754b7b835021676225ba235a82fb2d89",
    #"64996c3bdad619660de1236b82547e8421abeb7029630389cb1f7361",
    #"3e499ba0420b657eda31c61622a17c3d53edc1db0f5225022c3a2b00",
    #"9079019e845fe096bb3783b1ccfb0dc4f340ea1edeeb31c71d88a5cc",
  ]

/// `prefix` is a compile-time PARAMETER, applied with `aiken blueprint apply`. It does two
/// jobs at once: it forces every asset name under this policy to start with the series
/// ticker (so nobody can mint junk names under it), AND, because the parameter is baked into
/// the script, a different prefix yields a DIFFERENT POLICY ID. That is what lets a throwaway
/// test collection be minted end-to-end with identical logic, without ever touching the real
/// piece-9 policy.
validator gate(prefix: ByteArray) {
  mint(_redeemer: Data, own_policy: PolicyId, self: Transaction) {
    let Transaction { inputs, mint, .. } = self

    // (1) Exactly ONE asset under our own policy, quantity exactly 1. This is what keeps each
    //     mint a single NFT: no batch of a thousand in one transaction, and no burning either
    //     (a burn would carry a negative quantity and fail this pattern).
    expect [Pair(asset_name, 1)] = mint |> assets.tokens(own_policy) |> dict.to_pairs

    // (1b) The name must carry the series ticker. Also what makes the parameter load-bearing,
    //      so it cannot be optimised away and the test policy id genuinely differs.
    expect bytearray.take(asset_name, bytearray.length(prefix)) == prefix

    // (2) AT LEAST ONE of the eight earlier policies must appear among the SPENT inputs.
    //     Any piece will do; duplicates of one piece are as good as one of each.
    list.any(
      inputs,
      fn(i) {
        list.any(
          assets.policies(i.output.value),
          fn(p) { list.has(required, p) },
        )
      },
    )
  }

  else(_) {
    fail
  }
}

// ---------------------------------------------------------------------------------------
// Tests. The negative cases are the point: a gate that only proves it lets people IN has
// proved nothing. `aiken check` runs these.
// ---------------------------------------------------------------------------------------

const px: ByteArray = "PFP"

const own: PolicyId = #"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

fn addr() -> Address {
  Address {
    payment_credential: VerificationKey(
      #"00000000000000000000000000000000000000000000000000000000",
    ),
    stake_credential: None,
  }
}

/// One input holding a single NFT under `policy`.
fn utxo(policy: PolicyId, ix: Int) -> Input {
  Input {
    output_reference: OutputReference {
      transaction_id: #"0000000000000000000000000000000000000000000000000000000000000000",
      output_index: ix,
    },
    output: Output {
      address: addr(),
      value: assets.from_asset(policy, "piece", 1)
        |> assets.merge(assets.from_lovelace(1_180_000)),
      datum: NoDatum,
      reference_script: None,
    },
  }
}

/// A plain-ada input — what every real wallet spends alongside the piece.
fn ada_utxo(ix: Int) -> Input {
  Input {
    output_reference: OutputReference {
      transaction_id: #"1111111111111111111111111111111111111111111111111111111111111111",
      output_index: ix,
    },
    output: Output {
      address: addr(),
      value: assets.from_lovelace(5_000_000),
      datum: NoDatum,
      reference_script: None,
    },
  }
}

fn tx(inputs: List<Input>, mint: Value) -> Transaction {
  Transaction { ..placeholder, inputs: inputs, mint: mint }
}

fn all_eight() -> List<Input> {
  required |> list.indexed_map(fn(ix, p) { utxo(p, ix) })
}

fn one_nine() -> Value {
  assets.from_asset(own, "PFPdeadbeef", 1)
}

test passes_holding_all_eight() {
  gate.mint(px, Void, own, tx(all_eight(), one_nine()))
}

test passes_holding_only_the_first() {
  expect Some(first) = required |> list.head
  gate.mint(px, Void, own, tx([utxo(first, 0), ada_utxo(1)], one_nine()))
}

test passes_holding_only_the_last() {
  expect Some(last) = required |> list.last
  gate.mint(px, Void, own, tx([ada_utxo(0), utxo(last, 1)], one_nine()))
}

/// Any one piece will do — several copies of the same piece are as good as one.
test passes_with_eight_copies_of_one_piece() {
  expect Some(first) = required |> list.head
  let dupes = list.range(0, 7) |> list.map(fn(ix) { utxo(first, ix) })
  gate.mint(px, Void, own, tx(dupes, one_nine()))
}

test fails_holding_none() fail {
  gate.mint(px, Void, own, tx([ada_utxo(0)], one_nine()))
}

/// A piece in REFERENCE inputs must not count — referencing needs no signature, so anybody
/// could point at a stranger's wallet and mint.
test fails_when_the_piece_is_only_referenced() fail {
  expect Some(first) = required |> list.head
  let t =
    Transaction {
      ..placeholder,
      inputs: [ada_utxo(0)],
      reference_inputs: [utxo(first, 1)],
      mint: one_nine(),
    }
  gate.mint(px, Void, own, t)
}

/// An asset under a policy we do not require proves nothing.
test fails_with_only_an_impostor() fail {
  let impostor =
    utxo(#"ffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 99)
  gate.mint(px, Void, own, tx([impostor, ada_utxo(0)], one_nine()))
}

test fails_minting_two_of_the_ninth() fail {
  gate.mint(px, Void, own, tx(all_eight(), assets.from_asset(own, "PFPdeadbeef", 2)))
}

/// Two DIFFERENT assets under our own policy in one transaction must fail — one mint, one NFT.
test fails_minting_two_distinct_ninths() fail {
  let two =
    assets.from_asset(own, "PFPaaaa", 1)
      |> assets.merge(assets.from_asset(own, "PFPbbbb", 1))
  gate.mint(px, Void, own, tx(all_eight(), two))
}

/// Burning carries a negative quantity, so it fails the `1` pattern. Nothing under this policy
/// can ever be destroyed.
test fails_burning() fail {
  gate.mint(px, Void, own, tx(all_eight(), assets.from_asset(own, "PFPdeadbeef", -1)))
}

/// A name that does not carry the ticker must fail — this is what keeps junk assets out of
/// the policy, and it is what makes the parameter real rather than decorative.
test fails_with_a_foreign_asset_name() fail {
  gate.mint(px, Void, own, tx(all_eight(), assets.from_asset(own, "NOTMINE", 1)))
}
