"""Web3 smart contract deployment and testing."""
import os
from typing import Dict, Any, Optional, List

class ContractDeployer:
    def __init__(self, rpc_url: str = "", private_key: str = ""):
        self.rpc_url = rpc_url or os.getenv("WEB3_RPC_URL", "https://mainnet.infura.io/v3/YOUR_KEY")
        self.private_key = private_key or os.getenv("WEB3_PRIVATE_KEY")

    def compile(self, source: str) -> Dict[str, Any]:
        """Compile Solidity source."""
        try:
            from solcx import compile_source, install_solc
            install_solc("0.8.0")
            compiled = compile_source(source, output_values=["abi", "bin"])
            return {"abi": list(compiled.values())[0]["abi"], "bytecode": list(compiled.values())[0]["bin"]}
        except Exception as e:
            return {"error": str(e), "note": "Install py-solc-x: pip install py-solc-x"}

    def deploy(self, abi: List, bytecode: str, *args) -> Dict[str, Any]:
        """Deploy compiled contract."""
        try:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            contract = w3.eth.contract(abi=abi, bytecode=bytecode)
            tx = contract.constructor(*args).transact()
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            return {"address": receipt.contractAddress, "tx": tx.hex()}
        except Exception as e:
            return {"error": str(e), "note": "Install web3: pip install web3"}

    def call(self, address: str, abi: List, method: str, *args) -> Dict[str, Any]:
        """Call contract method."""
        try:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
            fn = getattr(contract.functions, method)
            return {"result": fn(*args).call()}
        except Exception as e:
            return {"error": str(e)}
