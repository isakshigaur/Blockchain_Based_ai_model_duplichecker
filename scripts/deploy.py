import json
import os
from pathlib import Path

from dotenv import load_dotenv
from solcx import compile_standard, install_solc
from web3 import Web3

load_dotenv()

CONTRACT_FILE = Path("contracts/ModelRegistry.sol")
ARTIFACT_FILE = Path("artifacts/ModelRegistry.json")
DEPLOYMENT_FILE = Path("artifacts/deployment.json")
SOLC_VERSION = "0.8.21"


def compile_contract():
    source = CONTRACT_FILE.read_text()
    install_solc(SOLC_VERSION)
    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {CONTRACT_FILE.name: {"content": source}},
            "settings": {
                "evmVersion": "paris",
                "outputSelection": {
                    "*": {
                        "*": [
                            "abi",
                            "metadata",
                            "evm.bytecode",
                            "evm.bytecode.sourceMap",
                        ]
                    }
                }
            },
        },
        solc_version=SOLC_VERSION,
    )

    contract_interface = compiled["contracts"][CONTRACT_FILE.name]["ModelRegistry"]
    abi = contract_interface["abi"]
    bytecode = contract_interface["evm"]["bytecode"]["object"]

    ARTIFACT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_FILE.write_text(json.dumps({"abi": abi, "bytecode": bytecode}, indent=2))
    return abi, bytecode


def deploy():
    rpc_url = os.getenv("RPC_URL", "http://127.0.0.1:8545")
    private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
    chain_id = int(os.getenv("CHAIN_ID", "1337"))

    if not private_key:
        raise ValueError("DEPLOYER_PRIVATE_KEY is required in the environment")

    abi, bytecode = compile_contract()
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        print(f"\nERROR: Cannot connect to RPC at {rpc_url}\n")
        if "127.0.0.1" in rpc_url or "localhost" in rpc_url:
            print("SOLUTION (Local):")
            print("1. Open a new terminal")
            print("2. Run: npx ganache-cli --chainId 1337 --port 8545 --deterministic")
            print("3. Keep that terminal open, then run this script again\n")
        else:
            print("SOLUTION (Sepolia / Remote):")
            print("1. Verify your RPC_URL in .env is correct")
            print("2. Check your Alchemy/Infura API key")
            print("3. Ensure you have internet connectivity\n")
        raise ConnectionError(f"Unable to connect to RPC at {rpc_url}")

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Check account balance
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, "ether")
    print(f"Deployer account: {account.address}")
    print(f"Account balance: {balance_eth} ETH")
    print(f"Chain ID: {chain_id}")
    print(f"Nonce: {nonce}")
    
    if balance == 0:
        print(f"\nERROR: Account {account.address} has 0 ETH.\n")
        if chain_id == 1337:
            print("SOLUTION (Ganache):")
            print("1. Check your Ganache terminal for 'Private Keys'")
            print("2. Copy the first private key")
            print("3. Update DEPLOYER_PRIVATE_KEY in .env\n")
        else:
            print("SOLUTION (Sepolia Testnet):")
            print("1. Go to https://cloud.google.com/application/web3/faucet/ethereum/sepolia")
            print(f"2. Paste your wallet address: {account.address}")
            print("3. Request free Sepolia ETH")
            print("4. Wait 1-2 minutes, then run this script again\n")
        raise ValueError("Account has 0 ETH.")

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    transaction = contract.constructor().build_transaction(
        {
            "chainId": chain_id,
            "from": account.address,
            "nonce": nonce,
            "gasPrice": w3.eth.gas_price,
        }
    )

    signed = account.sign_transaction(transaction)
    raw_tx = getattr(signed, "rawTransaction", None) or getattr(signed, "raw_transaction")
    tx_hash = w3.eth.send_raw_transaction(raw_tx)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    DEPLOYMENT_FILE.write_text(
        json.dumps(
            {
                "contractAddress": receipt.contractAddress,
                "transactionHash": receipt.transactionHash.hex(),
                "chainId": chain_id,
            },
            indent=2,
        )
    )

    print(f"Contract deployed to: {receipt.contractAddress}")
    return receipt.contractAddress


if __name__ == "__main__":
    deploy()

