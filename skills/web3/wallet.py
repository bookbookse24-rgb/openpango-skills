"""Wallet operations."""
import os
from typing import Dict, Any

class Wallet:
    def __init__(self, rpc_url: str = ""):
        self.rpc_url = rpc_url or os.getenv("WEB3_RPC_URL")

    def get_balance(self, address: str) -> Dict[str, Any]:
        try:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            bal = w3.eth.get_balance(Web3.to_checksum_address(address))
            return {"address": address, "balance_wei": bal, "balance_eth": float(Web3.from_wei(bal, "ether"))}
        except Exception as e:
            return {"error": str(e)}

    def send(self, to: str, amount_eth: float, private_key: str = "") -> Dict[str, Any]:
        try:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            account = w3.eth.account.from_key(private_key or os.getenv("WEB3_PRIVATE_KEY"))
            tx = {"to": to, "value": Web3.to_wei(amount_eth, "ether"), "gas": 21000, "nonce": w3.eth.get_transaction_count(account.address)}
            signed = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            return {"tx_hash": tx_hash.hex()}
        except Exception as e:
            return {"error": str(e)}
