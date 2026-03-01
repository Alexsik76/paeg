"""
Cryptography primitives for the voting protocols.
Provides utilities for RSA key generation, encryption, decryption, signing, and verification.
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


class RSACryptoSystem:
    def __init__(self, key_size: int = 2048):
        """
        Initialize the RSA Crypto System with a specific key size.
        """
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        self.public_key = self.private_key.public_key()

    def get_public_bytes(self) -> bytes:
        """Return the public key serialized to PEM format."""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def sign(self, message: bytes) -> bytes:
        """
        Sign a message with the private key.
        """
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return signature

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt a ciphertext using the private key.
        Uses hybrid encryption (RSA + AES via Fernet).
        """
        import json
        from cryptography.fernet import Fernet
        from base64 import b64decode

        try:
            payload = json.loads(ciphertext.decode("utf-8"))
            encrypted_key = b64decode(payload["key"])
            data = b64decode(payload["data"])

            aes_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            f = Fernet(aes_key)
            return f.decrypt(data)
        except Exception:
            # Fallback for standard RSA decrypt if it wasn't hybrid encrypted
            return self.private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

    @staticmethod
    def encrypt(public_key: rsa.RSAPublicKey, message: bytes) -> bytes:
        """
        Encrypt a message using a provided public key.
        Because RSA has a strict message size limit depending on key size,
        we use hybrid encryption: AES (Fernet) for the data, and RSA for the AES key.
        """
        import json
        from cryptography.fernet import Fernet
        from base64 import b64encode

        # Generate a random AES key for Fernet
        aes_key = Fernet.generate_key()
        f = Fernet(aes_key)

        # Encrypt the actual message with AES
        ciphertext = f.encrypt(message)

        # Encrypt the AES key with RSA
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Combine both into a JSON payload
        hybrid_payload = {
            "key": b64encode(encrypted_key).decode("utf-8"),
            "data": b64encode(ciphertext).decode("utf-8"),
        }
        return json.dumps(hybrid_payload).encode("utf-8")

    @staticmethod
    def verify(public_key: rsa.RSAPublicKey, message: bytes, signature: bytes) -> bool:
        """
        Verify a signature using a provided public key.
        """
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def load_public_key(pem_data: bytes) -> rsa.RSAPublicKey:
        """
        Load a public key from PEM formatted bytes.
        """
        return serialization.load_pem_public_key(pem_data)
