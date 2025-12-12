import hashlib
import time

class ProofOfHelpContract:
    """
    Stub blockchain client to record proofs of help.
    In production, replace with real web3 client integration.
    """

    def record_help(self, issue_id: int, volunteer_address: str, station_id: int, proof_hash: str, points: int) -> str:
        payload = f"{issue_id}:{volunteer_address}:{station_id}:{proof_hash}:{points}:{int(time.time())}"
        # Return a deterministic pseudo tx hash for now
        return hashlib.sha256(payload.encode()).hexdigest()
