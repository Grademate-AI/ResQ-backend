import json
from pathlib import Path
from django.conf import settings
from .web3 import w3

BASE_DIR = Path(__file__).resolve().parent

def load_contract(name, address):
    abi_path = BASE_DIR / "abis" / f"{name}.json"
    abi = json.loads(abi_path.read_text())["abi"]
    return w3.eth.contract(address=address, abi=abi)

reward_token = load_contract("RewardToken", settings.REWARD_TOKEN_ADDRESS)
sbt = load_contract("SoulboundBadge", settings.SBT_ADDRESS)
proof = load_contract("ProofOfHelp", settings.PROOF_OF_HELP_ADDRESS)