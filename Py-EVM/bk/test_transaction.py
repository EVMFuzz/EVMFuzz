import os
import sys
import argparse

from eth_utils import (
    decode_hex,
    to_canonical_address,
    to_wei,
    to_bytes,
)

from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.byzantium import ByzantiumVM

from eth.db.backends.memory import MemoryDB
from eth_keys import keys
from eth_typing import Address

from tests.core.helpers import (
    new_transaction,
)
from cytoolz import (
    assoc,
)

GENESIS_PARAMS = {
     'parent_hash': constants.GENESIS_PARENT_HASH,
     'uncles_hash': constants.EMPTY_UNCLE_HASH,
     'coinbase': constants.ZERO_ADDRESS,
     'transaction_root': constants.BLANK_ROOT_HASH,
     'receipt_root': constants.BLANK_ROOT_HASH,
     'difficulty': 1,
     'block_number': constants.GENESIS_BLOCK_NUMBER,
     'gas_limit': constants.GENESIS_GAS_LIMIT,
     'timestamp': 1514764800,
     'extra_data': constants.GENESIS_EXTRA_DATA,
     'nonce': constants.GENESIS_NONCE
}

def funded_address_private_key():
    return keys.PrivateKey(
        decode_hex('0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8')
    )

BYTECODE="60606040526103dd806100126000396000f360606040526000357c010000000000000000000000000000000000000000000000000000000090048063454a2ab31461004f578063b9a2de3a14610091578063edd481bb146100d35761004d565b005b6100656004808035906020019091905050610189565b604051808273ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6100a760048080359060200190919050506102d2565b604051808273ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6100e960048080359060200190919050506100ff565b6040518082815260200191505060405180910390f35b600060016000818150548092919060010191905055905080508143016000600050600083815260200190815260200160002060005060000160005081905550336000600050600083815260200190815260200160002060005060030160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908302179055505b919050565b60006000600060005060008481526020019081526020016000206000509050346012600a8360010160005054011811806101c95750438160000160005054115b1561022d573373ffffffffffffffffffffffffffffffffffffffff16600034604051809050600060405180830381858888f19350505050508060020160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1691506102cc565b8060020160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1660008260010160005054604051809050600060405180830381858888f1935050505050338160020160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908302179055503481600101600050819055503391506102cc565b50919050565b600060006000600050600084815260200190815260200160002060005090508060000160005054431015156103d6578060030160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1660008260010160005054604051809050600060405180830381858888f19350505050506000816001016000508190555060008160020160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908302179055506000816000016000508190555060008160030160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908302179055505b5b5091905056"
DATA="0x454a2ab30000000000000000000000000000000000000000000000000000000000000045"
   
RECEIVER = to_canonical_address("0x692a70d2e424a56d2c6c27aa97d1a86395877b3a")

SENDER_PRIVATE_KEY = funded_address_private_key()
# SENDER = to_canonical_address("0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b")
SENDER = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

def funded_address_initial_balance():
    return to_wei(1000, 'ether')

def base_genesis_state(funded_address, funded_address_initial_balance):
    return {
        funded_address: {
            'balance': funded_address_initial_balance,
            'nonce': 0,
            'code': b'',
            'storage': {},
        }
    }
    
def genesis_state(base_genesis_state, simple_contract_address):
    return assoc(
        base_genesis_state,
        simple_contract_address,
        {
            'balance': 0,
            'nonce': 0,
            'code': decode_hex(BYTECODE),  # contract bytecode
            'storage': {},
        },
    )
    
def main ():
    # genesis address
    init_address = to_canonical_address("8888f1f195afa192cfee860698584c030f4c9db1")
    base_state = base_genesis_state(init_address, funded_address_initial_balance())
    
    simple_contract_address = RECEIVER

    # create chain
    klass = MiningChain.configure(
        __name__='MyTestChain',
        vm_configuration=(
            (constants.GENESIS_BLOCK_NUMBER, ByzantiumVM),
        ))
    chain = klass.from_genesis(MemoryDB(), GENESIS_PARAMS, 
                               genesis_state(base_state, simple_contract_address))
    # chain = klass.from_genesis(MemoryDB(), GENESIS_PARAMS, base_state)
    vm = chain.get_vm()

    # tx = vm.create_unsigned_transaction(
    #       nonce=vm.state.account_db.get_nonce(SENDER),
    #       gas_price=0x1,
    #       gas=0x90710,
    #       to=simple_contract_address,
    #       value=0x10,
    #       data=DATA.encode(),
    # )
    # signed_tx = tx.as_signed_transaction(SENDER_PRIVATE_KEY)
    # _, _, computation = chain.apply_transaction(signed_tx, 0x90777)
    
    call_txn = new_transaction(
        vm,
        SENDER,
        RECEIVER,
        amount=0x10,
        data=DATA.encode(),
    )
    result_bytes = chain.get_transaction_result(call_txn, chain.get_canonical_head(), 1000)
    # print("* result_bytes : {}".format(result_bytes))


if __name__ == '__main__':
    main()

