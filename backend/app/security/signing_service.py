import base64
import json
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


def ensure_key_pair(base_dir):
    key_dir = Path(base_dir)
    key_dir.mkdir(parents=True, exist_ok=True)
    priv_path = key_dir / "private_key.pem"
    pub_path = key_dir / "public_key.pem"

    if not priv_path.exists() or not pub_path.exists():
        private_key = ec.generate_private_key(ec.SECP256R1())
        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        priv_path.write_bytes(priv_bytes)
        pub_path.write_bytes(pub_bytes)

    return str(priv_path), str(pub_path)


def load_private_key(key_path):
    return serialization.load_pem_private_key(Path(key_path).read_bytes(), password=None)


def load_public_key(key_path):
    return serialization.load_pem_public_key(Path(key_path).read_bytes())


def sign_payload(payload_dict, key_path):
    private_key = load_private_key(key_path)
    payload_json = json.dumps(payload_dict, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = private_key.sign(payload_json, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature).decode("utf-8")


def verify_signature(payload_dict, signature, public_key_path):
    try:
        public_key = load_public_key(public_key_path)
        payload_json = json.dumps(payload_dict, sort_keys=True, separators=(",", ":")).encode("utf-8")
        public_key.verify(base64.b64decode(signature), payload_json, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False
