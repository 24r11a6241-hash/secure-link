# 🔐 SecureLink E2EE — Zero-Trust Hybrid Cryptographic Messenger

A real-time messaging application demonstrating **End-to-End Encryption (E2EE)** using hybrid cryptography: RSA-2048 with OAEP padding and AES-256-GCM. The server acts as a blind relay, forwarding encrypted payloads without accessing message plaintext.

## ✨ Features

- **RSA-2048 OAEP:** Protects AES encryption keys using the recipient's public key.
- **AES-256-GCM:** Encrypts messages and verifies their integrity.
- **Blind Relay Server:** Provides public-key directory services and forwards encrypted payloads.
- **Real-Time Messaging:** Supports communication between terminal clients using Socket.IO.
- **Client-Side Cryptography:** Performs message encryption and decryption on user devices.
- **Self-Test:** Includes a cryptographic test in `crypto_engine.py`.

## 📁 Project Structure

- `crypto_engine.py` — Key generation, hybrid encryption/decryption, and self-test.
- `server_relay.py` — FastAPI and Socket.IO directory and relay server.
- `network_client.py` — Terminal client for real-time messaging.
- `requirements.txt` — Python dependencies.

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the cryptographic self-test

```bash
python crypto_engine.py
```

### 3. Start the relay server

Open Terminal 1:

```bash
python server_relay.py
```

### 4. Start two clients

Open Terminal 2:

```bash
python network_client.py alice
```

Open Terminal 3:

```bash
python network_client.py bob
```

Follow the client prompts to exchange messages. For example, Bob can send:

```text
alice: hello
```

## 🔒 How It Works

1. Users generate cryptographic keys on their devices and register their public keys.
2. The sender generates a fresh AES key and encrypts the message using AES-256-GCM.
3. RSA-OAEP encrypts the AES key using the recipient's public key.
4. The server relays the encrypted payload to the recipient.
5. The recipient uses their RSA private key to recover the AES key and decrypt the message.

## ⚠️ Known Limitations

- **Public-key authentication:** The server distributes public keys without authentication, allowing a malicious server to substitute keys and potentially perform a man-in-the-middle attack.
- **No digital signatures:** Recipients cannot cryptographically prove the sender's identity.
- **No forward secrecy:** Static RSA keys are used in this design.
- **No offline message queue:** Offline recipients cannot receive queued messages.
- **In-memory storage:** Data is not persistently stored.
- **Key persistence:** Keys are regenerated each run, according to the project design.
- **Demo configuration:** CORS is open, and the server binds to localhost.

These limitations make the current implementation suitable for educational demonstrations rather than production deployment.

## 🔮 Future Enhancements

- Public-key fingerprint verification or safety numbers.
- Digital signatures for sender authentication.
- Forward secrecy using an appropriate authenticated key-agreement protocol.
- Secure key storage and persistence.
- Offline message delivery and improved access controls.

## 🛠️ Technology Stack

Python · PyCryptodome · FastAPI · Socket.IO · RSA · AES-GCM

## 🎯 Objective

To demonstrate how hybrid cryptography and client-side encryption can protect message confidentiality and integrity while allowing a server to route encrypted communications.

## 👨‍💻 Author

**P. Nikhil**

---

*SecureLink E2EE — Your messages, your privacy.*
