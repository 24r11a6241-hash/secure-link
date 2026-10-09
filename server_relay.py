import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import socketio

app = FastAPI(title="SecureLink E2EE Blind Directory Server")
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# In-memory storage maps
USER_PUBLIC_KEYS = {}   # { username: public_key_pem }
ACTIVE_CONNECTIONS = {}  # { username: sid }


class RegisterKeyModel(BaseModel):
    username: str
    public_key_pem: str


@app.post("/register")
async def register_public_identity(data: RegisterKeyModel):
    if data.username in USER_PUBLIC_KEYS:
        raise HTTPException(status_code=400, detail="Username already claimed.")
    USER_PUBLIC_KEYS[data.username] = data.public_key_pem
    return {"status": "success", "message": f"Identity registered for {data.username}"}


@app.get("/get_key/{username}")
async def fetch_public_identity(username: str):
    if username not in USER_PUBLIC_KEYS:
        raise HTTPException(status_code=404, detail="User identity profile not found.")
    return {"username": username, "public_key_pem": USER_PUBLIC_KEYS[username]}


@sio.event
async def connect(sid, environ):
    print(f"[+] Client Socket Connected: {sid}")


@sio.event
async def register_session(sid, data):
    username = data.get("username")
    if username:
        ACTIVE_CONNECTIONS[username] = sid
        print(f"[+] User Session Linked: {username} maps to SID {sid}")


@sio.event
async def route_secure_payload(sid, data):
    sender = data.get("sender")
    recipient = data.get("recipient")
    encrypted_msg = data.get("encrypted_payload")

    recipient_sid = ACTIVE_CONNECTIONS.get(recipient)
    if recipient_sid:
        await sio.emit(
            "incoming_secure_payload",
            {"sender": sender, "encrypted_payload": encrypted_msg},
            to=recipient_sid,
        )
        print(f"[🛡️] Secure encrypted payload routed: [{sender}] -> [{recipient}]")
    else:
        print(f"[!] Routing Failure: User [{recipient}] is currently offline.")


@sio.event
async def disconnect(sid):
    for username, mapped_sid in list(ACTIVE_CONNECTIONS.items()):
        if mapped_sid == sid:
            del ACTIVE_CONNECTIONS[username]
            print(f"[-] User Session Severed: {username}")
            break


if __name__ == "__main__":
    uvicorn.run(socket_app, host="127.0.0.1", port=8000)
