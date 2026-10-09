import base64
import json

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes


class SecureClientCrypto:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.generate_new_keypair()

    def generate_new_keypair(self):
        """Generates a local RSA-2048 keypair. Private key never leaves the client."""
        key = RSA.generate(2048)
        self.private_key = key
        self.public_key = key.publickey()

    def get_public_key_pem(self) -> str:
        """Exports the public key to PEM format for server distribution."""
        return self.public_key.export_key().decode("utf-8")

    def encrypt_message(self, plaintext: str, recipient_public_key_pem: str) -> str:
        """
        Hybrid Encryption Scheme:
        1. Generates a unique AES-256 session key.
        2. Encrypts the plaintext message with AES-GCM.
        3. Encrypts the AES key with the recipient's RSA public key.
        """
        aes_key = get_random_bytes(32)
        aes_cipher = AES.new(aes_key, AES.MODE_GCM)
        ciphertext_bytes, auth_tag = aes_cipher.encrypt_and_digest(plaintext.encode("utf-8"))

        recipient_key = RSA.import_key(recipient_public_key_pem)
        rsa_cipher = PKCS1_OAEP.new(recipient_key)
        encrypted_aes_key = rsa_cipher.encrypt(aes_key)

        payload = {
            "nonce": base64.b64encode(aes_cipher.nonce).decode("utf-8"),
            "tag": base64.b64encode(auth_tag).decode("utf-8"),
            "ciphertext": base64.b64encode(ciphertext_bytes).decode("utf-8"),
            "encrypted_key": base64.b64encode(encrypted_aes_key).decode("utf-8"),
        }
        return json.dumps(payload)

    def decrypt_message(self, encrypted_payload_json: str) -> str:
        """
        Hybrid Decryption Sequence:
        1. Unwraps the AES key using the local RSA private key.
        2. Decrypts and verifies the ciphertext via AES-GCM parameters.
        """
        payload = json.loads(encrypted_payload_json)

        nonce = base64.b64decode(payload["nonce"])
        auth_tag = base64.b64decode(payload["tag"])
        ciphertext = base64.b64decode(payload["ciphertext"])
        encrypted_key = base64.b64decode(payload["encrypted_key"])

        rsa_cipher = PKCS1_OAEP.new(self.private_key)
        aes_key = rsa_cipher.decrypt(encrypted_key)

        aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext_bytes = aes_cipher.decrypt_and_verify(ciphertext, auth_tag)

        return plaintext_bytes.decode("utf-8")


if __name__ == "__main__":
    print("[*] Running Cryptographic Simulation Validation...")
    alice = SecureClientCrypto()
    bob = SecureClientCrypto()

    msg = "Confidential Capstone Project Data: Clear for Launch."
    print(f"Original Plaintext: {msg}")

    encrypted_data = bob.encrypt_message(msg, alice.get_public_key_pem())
    print(f"\nIntercepted Ciphertext (Server Payload View):\n{encrypted_data}\n")

    decrypted_data = alice.decrypt_message(encrypted_data)
    print(f"Decrypted Result: {decrypted_data}")
    assert decrypted_data == msg
    print("[+] Validation passed.")
