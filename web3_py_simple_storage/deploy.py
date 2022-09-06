from web3 import Web3

from solcx import compile_standard, install_solc
import json
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

print("Installing...")
install_solc("0.6.0")
# Compile Our Solididty
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
# print(compiled_sol)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to Goerli
w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/14beebc7b6f145c2888d247a01a08c32"))
chain_id = 5
my_address = "0xd720BBF165657d7efd101DF859dc4d3d3500Ab83"
private_key = os.getenv("PRIVATE_KEY")
# print(private_key)
# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# print(nonce)
# print(nounce)
# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": my_address, "nonce": nonce,}
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(os.getenv("SOME_OTHER_VAR")) # testing purpose
# print(signed_txn)

# send this signed transaction
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# Working with the contract, you always need
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change

#  Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating Contract...")
# print(simple_storage.functions.store(8).call())
# print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(8).buildTransaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": my_address, "nonce": nonce + 1}
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx) # sends the transaction to a block chain
print("Updated!")
print(simple_storage.functions.retrieve().call())