from .contracts import proof
from .tx_helpers import build_sign_send_tx
from .web3 import w3
from django.conf import settings

def send_record_help(
    *,
    issue_id: int,
    volunteer_address: str,
    ngo_address: str,
    station_id: int,
    proof_hash: str,
    points: int
):
    nonce = w3.eth.get_transaction_count(settings.DEPLOYER_ADDRESS)

    tx = proof.functions.recordHelp(
        issue_id,
        volunteer_address,
        ngo_address,
        station_id,
        proof_hash,
        points
    ).build_transaction({
        "from": settings.DEPLOYER_ADDRESS,
        "nonce": nonce,
        "gas": 400_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": settings.CHAIN_ID
    })

    receipt = build_sign_send_tx(tx)
    return receipt


def deposit_ngo_funds(amount_wei):
    nonce = w3.eth.get_transaction_count(settings.DEPLOYER_ADDRESS)

    tx = proof.functions.depositFunds().build_transaction({
        "from": settings.DEPLOYER_ADDRESS,
        "nonce": nonce,
        "value": amount_wei,
        "gas": 200_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": settings.CHAIN_ID
    })

    return build_sign_send_tx(tx)


def get_ngo_balance(ngo_address):
    return proof.functions.getNGOBalance(ngo_address).call()