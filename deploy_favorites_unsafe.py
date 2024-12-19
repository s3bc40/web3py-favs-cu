from web3 import Web3, HTTPProvider
from vyper import compile_code
from dotenv import load_dotenv
import os

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
MY_ADDRESS = os.getenv("MY_ADDRESS")

def main():
    print("Let's read in the Vyper code and deploy it to the blockchain!")
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    with open("favorites.vy", "r") as favorites_file:
        favorites_code = favorites_file.read()
        compilation_details = compile_code(
            favorites_code, output_formats=["bytecode", "abi"]
        )

    chain_id = 31337  # Make sure this matches your virtual or anvil network!

    # Create the contract in Python
    favorites_contract = w3.eth.contract(
        abi=compilation_details["abi"], bytecode=compilation_details["bytecode"]
    )

    # Submit the transaction that deploys the contract
    nonce = w3.eth.get_transaction_count(MY_ADDRESS)

    print("Building the transaction...")
    transaction = favorites_contract.constructor().build_transaction(
        {
            "gasPrice": w3.eth.gas_price,
            "from": MY_ADDRESS,
            "nonce": nonce,
        }
    )

    print("Signing transaction")
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
    
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"My tx hash: {tx_hash}")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Contract deployed to {tx_receipt.contractAddress}")

if __name__ == "__main__":
    main()