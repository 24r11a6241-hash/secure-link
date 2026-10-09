"""
Terminal chat client for SecureLink E2EE.
Usage:  python network_client.py <your_username> [server_url]
Then type:  recipient: message     (e.g.  bob: hello there)
"""
import sys
import threading

import requests
import socketio

from crypto_engine import SecureClientCrypto

if len(sys.argv) < 2:
    print("Usage: python network_client.py <username> [server_url]")
    sys.exit(1)

USERNAME = sys.argv[1]
SERVER = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8000"

crypto = SecureClientCrypto()
sio = socketio.Client()


@sio.event
def connect():
    sio.emit("register_session", {"username": USERNAME})
    print(f"[+] Connected as {USERNAME}. Type 'recipient: message' (Ctrl+C to quit).")


@sio.on("incoming_secure_payload")
def on_payload(data):
    try:
        text = crypto.decrypt_message(data["encrypted_payload"])
        print(f"\n[{data['sender']}] {text}\n> ", end="", flush=True)
    except Exception as exc:
        print(f"\n[!] Rejected message from {data.get('sender')}: {exc}\n> ", end="", flush=True)


def register():
    r = requests.post(f"{SERVER}/register",
                      json={"username": USERNAME, "public_key_pem": crypto.get_public_key_pem()})
    if r.status_code != 200:
        print(f"[!] Registration failed: {r.json().get('detail')}")
        sys.exit(1)


def send(recipient, text):
    r = requests.get(f"{SERVER}/get_key/{recipient}")
    if r.status_code != 200:
        print(f"[!] {r.json().get('detail')}")
        return
    payload = crypto.encrypt_message(text, r.json()["public_key_pem"])
    sio.emit("route_secure_payload",
             {"sender": USERNAME, "recipient": recipient, "encrypted_payload": payload})


if __name__ == "__main__":
    register()
    sio.connect(SERVER)
    try:
        while True:
            line = input("> ").strip()
            if ":" not in line:
                print("Format: recipient: message")
                continue
            to, msg = line.split(":", 1)
            send(to.strip(), msg.strip())
    except (KeyboardInterrupt, EOFError):
        sio.disconnect()
