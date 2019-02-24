import os
import sys
import argparse

from eth_utils import (
    decode_hex,
    function_signature_to_4byte_selector,
    function_abi_to_4byte_selector,
    to_canonical_address,
    to_wei,
    to_bytes,
)

from eth import constants
from eth.chains.base import MiningChain
from eth.vm.forks.byzantium import ByzantiumVM
from eth.vm.forks.spurious_dragon import SpuriousDragonVM

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

def create_simple_contract_address():
    return b'\x88' * 20

def funded_address_private_key():
    return keys.PrivateKey(
        decode_hex('0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8')
    )


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Test a transaction')

    # contract runtime bytecode  $ solc xxx.sol --bin-runtime
    parser.add_argument('--data', dest='data', default='608060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806324ff38a214610046575b600080fd5b34801561005257600080fd5b5061005b6100d6565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561009b578082015181840152602081019050610080565b50505050905090810190601f1680156100c85780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b60606040805190810160405280601781526020017fd0a5d18dd0bbd0bbd0bed18320d092d0bed180d0bbd0b40000000000000000008152509050905600a165627a7a723058203be6e0bef1136b3990b584f8793a7580eac61300597fe935cb30a719d80c17b60029', type=str)
    # function signature bytecode
    parser.add_argument('--sig', dest='signature', default='0x24ff38a2', type=str)

    args = parser.parse_args()
    return args

SENDER_PRIVATE_KEY = funded_address_private_key()
SENDER = Address(SENDER_PRIVATE_KEY.public_key.to_canonical_address())

# SENDER = to_canonical_address("0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b")
# RECEIVER = to_canonical_address("0x692a70d2e424a56d2c6c27aa97d1a86395877b3a")

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
    
def genesis_state(base_genesis_state, simple_contract_address, bytecode):
    return assoc(
        base_genesis_state,
        simple_contract_address,
        {
            'balance': 0,
            'nonce': 0,
            'code': decode_hex(bytecode),  # contract bytecode
            'storage': {},
        },
    )

def uint256_to_bytes(uint):
    return to_bytes(uint).rjust(32, b'\0')
    
def bytes_to_uint256(bytes):
    remove_str = bytes.decode().lstrip('\0')
    # print(remove_str)
    byte_str = remove_str.encode()
    # print(byte_str)
    uint = int.from_bytes(byte_str, byteorder='little')
    return uint

def main ():
    args = parse_args()
    # print('Called with args:')
    # print(args)

    # genesis address
    init_address = to_canonical_address("8888f1f195afa192cfee860698584c030f4c9db1")
    base_state = base_genesis_state(init_address, funded_address_initial_balance())
    
    # just an address
    simple_contract_address = create_simple_contract_address()

    # create chain
    klass = MiningChain.configure(
        __name__='MyTestChain',
        vm_configuration=(
            (constants.GENESIS_BLOCK_NUMBER, SpuriousDragonVM),
        ),
        network_id=1337,
    )
    chain = klass.from_genesis(MemoryDB(), GENESIS_PARAMS, 
                  genesis_state(base_state, simple_contract_address, args.data))

    # TODO
    # signature = 'getMeaningOfLife()'  # function name
    # function_selector = function_signature_to_4byte_selector(signature)
    '''
		new_transaction(
		    vm,
		    from_,
		    to,
		    amount=0,
		    private_key=None,
		    gas_price=10,
		    gas=100000,
		    data=b''
		)
    '''
    call_txn = new_transaction(
        chain.get_vm(),
        SENDER,
        simple_contract_address,
        gas_price=0,
        # data=function_selector,
        data=decode_hex(args.signature),
    )
    result_bytes = chain.get_transaction_result(call_txn, chain.get_canonical_head())

if __name__ == '__main__':
    # usage: test_tx.py [-h] [--data DATA] [--sig SIGNATURE]
    main()

