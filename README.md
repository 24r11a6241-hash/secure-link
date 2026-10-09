# SecureLink E2EE — Zero-Trust Hybrid Cryptographic Messenger

Hybrid encryption (RSA-2048 OAEP + AES-256-GCM) with a blind relay server.

## Files
- `crypto_engine.py` – client crypto (keygen, hybrid encrypt/decrypt) + self-test
- `server_relay.py`  – FastAPI + Socket.IO directory/relay (never sees plaintext)
- `network_client.py` – terminal chat client for live demo
- `requirements.txt`

## Run
    pip install -r requirements.txt
    python crypto_engine.py          # self-test
    python server_relay.py           # terminal 1
    python network_client.py alice   # terminal 2
    python network_client.py bob     # terminal 3
    # in bob's terminal:  alice: hello

## Known limitations (good to state to reviewers)
- The server distributes public keys without authentication, so a malicious server could
  substitute keys (MitM). Real systems add key fingerprints / safety numbers verified out-of-band.
- No sender signatures: a recipient can't cryptographically prove who sent a message.
- No forward secrecy (static RSA keys); no offline message queue; in-memory storage only.
- Keys are regenerated each run; CORS is open and the server binds to localhost – demo use only.
