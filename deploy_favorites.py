# web3
from web3 import Web3, HTTPProvider
from eth_account import Account
from vyper import compile_code
# python
from dotenv import load_dotenv
import os
import sys
import getpass
from pathlib import Path
import json

# Load environment variables
load_dotenv()
RPC_URL = os.getenv("RPC_URL")
MY_ANVIL_ADDRESS = os.getenv("MY_ANVIL_ADDRESS")
TENDERLY_RPC_URL = os.getenv("TENDERLY_RPC_URL")
METAMASK_ADDRESS = os.getenv("METAMASK_ADDRESS")

# Get args
CHAIN_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 31337

# Get keystore account
KEYSTORE_PATH = Path(".keystore.json")

def network_helper(chain_id: int) -> tuple([str, str]):
    address = None
    rpc_url = None
    if chain_id == 735711155111:
        # Tenderly
        address = METAMASK_ADDRESS
        rpc_url = TENDERLY_RPC_URL
    else:
        # Anvil
        address = MY_ANVIL_ADDRESS
        rpc_url = RPC_URL
    return (address, rpc_url)

def main() -> None:
    # No chain id passed in
    if CHAIN_ID == None:
        print("Please pass in a chain id")
        return
    elif CHAIN_ID != 735711155111 and CHAIN_ID != 31337:
        print("Please pass in a valid chain id")
        return
    
    print(f"Deploying to chain id: {CHAIN_ID}")
    # Run on the correct network
    print("Let's read in the Vyper code and deploy it to the blockchain!")
    (address, rpc_url) =  network_helper(CHAIN_ID)
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    with open("favorites.vy", "r") as favorites_file:
        favorites_code = favorites_file.read()
        compilation_details = compile_code(
            favorites_code, output_formats=["bytecode", "abi"]
        )

    # Create the contract in Python
    favorites_contract = w3.eth.contract(
        abi=compilation_details["abi"], bytecode=compilation_details["bytecode"]
    )

    # Submit the transaction that deploys the contract
    nonce = w3.eth.get_transaction_count(address)

    print("Building the transaction...")
    transaction = favorites_contract.constructor().build_transaction(
        {
            "gasPrice": w3.eth.gas_price,
            "from": address,
            "nonce": nonce,
        }
    )

    # Decrypt account
    if not KEYSTORE_PATH.exists():
        print("Please run encrypt_key.py first")
        return

    with KEYSTORE_PATH.open("r") as fp:
        encrypted_account = json.load(fp)
        passphrase = getpass.getpass("Enter passphrase of your wallet account:")
        private_key = Account.decrypt(encrypted_account, passphrase)
    
    print("Signing transaction")
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"My tx hash: {tx_hash}")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Contract deployed to {tx_receipt.contractAddress}")

if __name__ == "__main__":
    main()