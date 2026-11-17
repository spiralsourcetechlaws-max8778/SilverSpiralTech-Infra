import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from sliver import SliverClientConfig, SliverClient

load_dotenv()

app = FastAPI(title="SilverSpiralTech Bridge")
CONFIG_PATH = os.getenv("SLIVER_CONFIG", "/root/SilverSpiralTech/bridge/operator.cfg")
BRIDGE_API_KEY = os.getenv("BRIDGE_API_KEY")

client = None

class CommandRequest(BaseModel):
    session_id: str
    command: str
    args: list = []

def verify_key(x_api_key: str):
    if x_api_key != BRIDGE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid Bridge API Key")

@app.on_event("startup")
async def startup_event():
    global client
    if not os.path.exists(CONFIG_PATH):
        print(f"⚠️ WARNING: {CONFIG_PATH} not found. Awaiting operator.cfg from VPS.")
        return
    try:
        config = SliverClientConfig.parse_config_file(CONFIG_PATH)
        client = SliverClient(config)
        await client.connect()
        print("✅ Connected to Remote Sliver Server via gRPC")
    except Exception as e:
        print(f"❌ Failed to connect to Sliver: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "sliver_connected": client is not None}

@app.get("/sessions")
async def list_sessions(x_api_key: str = Header(None)):
    verify_key(x_api_key)
    if not client:
        raise HTTPException(status_code=503, detail="Sliver client not connected")
    sessions = await client.sessions()
    beacons = await client.beacons()
    return {
        "sessions": [{"id": s.ID, "hostname": s.Hostname, "os": s.OS, "user": s.Username} for s in sessions],
        "beacons": [{"id": b.ID, "hostname": b.Hostname, "os": b.OS, "last_checkin": str(b.LastCheckin)} for b in beacons]
    }

@app.post("/command")
async def execute_command(req: CommandRequest, x_api_key: str = Header(None)):
    verify_key(x_api_key)
    if not client:
        raise HTTPException(status_code=503, detail="Sliver client not connected")
    interact = await client.interact_session(req.session_id)
    result = await interact.execute(req.command, req.args)
    return {"stdout": result.Stdout.decode('utf-8'), "stderr": result.Stderr.decode('utf-8')}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
