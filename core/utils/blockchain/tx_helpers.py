from .web3 import w3
from django.conf import settings

def build_sign_send_tx(tx):
    signed = w3.eth.account.sign_transaction(
        tx,
        private_key=settings.DEPLOYER_PRIVATE_KEY
    )
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt