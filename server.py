"""
Soundpad Launcher - Backend Server
Communicates with Soundpad via Named Pipe API
"""

import json
import os
import struct
import time
from pathlib import Path
from typing import Optional
import asyncio

try:
    import win32file
    import win32pipe
    WINDOWS = True
except ImportError:
    WINDOWS = False

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Soundpad Launcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Support both standalone (python server.py) and launcher (.exe) modes
_data_root = Path(os.environ.get('SL_DATA_PATH', '.'))
_static_root = Path(os.environ.get('SL_STATIC_PATH', 'static'))
DATA_FILE = _data_root / "data" / "sounds.json"
UPLOAD_DIR = _data_root / "static" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

SOUNDPAD_PIPE = r"\\.\pipe\sp_remote_control"


# ─── Soundpad Named Pipe Communication ───────────────────────────────────────

def soundpad_call(command: str) -> str:
    """Send a command to Soundpad via Named Pipe and return response."""
    if not WINDOWS:
        return f"[DEV MODE] Would send: {command}"
    try:
        handle = win32file.CreateFile(
            SOUNDPAD_PIPE,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )
        encoded = (command + "\0").encode("utf-8")
        win32file.WriteFile(handle, encoded)
        _, data = win32file.ReadFile(handle, 4096)
        win32file.CloseHandle(handle)
        return data.decode("utf-8").rstrip("\0")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Soundpad connection failed: {str(e)}")


def sp_play_sound(index: int) -> str:
    return soundpad_call(f"DoPlaySound({index})")

def sp_stop_sound() -> str:
    return soundpad_call("DoStopSound()")

def sp_get_sound_list() -> str:
    return soundpad_call("GetSoundlist()")

def sp_get_playback_status() -> str:
    return soundpad_call("GetPlayStatus()")

def sp_set_volume(volume: int) -> str:
    return soundpad_call(f"DoSetSoundboardVolume({volume})")


# ─── Data Management ─────────────────────────────────────────────────────────

def load_data() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sounds": [], "categories": ["Genel"], "settings": {"volume": 100}}

def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class SoundEntry(BaseModel):
    id: str
    name: str
    soundpad_index: int
    category: str = "Genel"
    image: Optional[str] = None
    play_count: int = 0
    is_favorite: bool = False
    color: Optional[str] = None
    last_played: Optional[float] = None

class SoundUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    is_favorite: Optional[bool] = None
    color: Optional[str] = None
    soundpad_index: Optional[int] = None
    spam_interval: Optional[int] = None
    spam_count: Optional[int] = None
    unavailable: Optional[bool] = None

class PlayRequest(BaseModel):
    sound_id: str

class VolumeRequest(BaseModel):
    volume: int

class AddSoundRequest(BaseModel):
    name: str
    soundpad_index: int
    category: str = "Genel"

class CategoryRequest(BaseModel):
    name: str

class ReorderRequest(BaseModel):
    sound_ids: list[str]


# ─── API Endpoints ───────────────────────────────────────────────────────────

def auto_validate():
    """Auto-validate sounds against Soundpad list. Returns changed count."""
    try:
        raw = sp_get_sound_list()
        import re
        indexes = set(int(m) for m in re.findall(r"index=\"(\d+)\"", raw))
        data = load_data()
        changed = 0
        for sound in data["sounds"]:
            was = sound.get("unavailable", False)
            now = sound["soundpad_index"] not in indexes
            if was != now:
                sound["unavailable"] = now
                changed += 1
        if changed:
            save_data(data)
        return changed
    except:
        return 0

@app.get("/api/status")
async def get_status():
    """Check if Soundpad is running, auto-validate sounds"""
    try:
        status = sp_get_playback_status()
        changed = auto_validate()
        return {"connected": True, "status": status, "windows": WINDOWS, "validated": True, "changed": changed}
    except Exception as e:
        err = str(e)
        if "503" in err or "pipe" in err.lower() or "soundpad" in err.lower():
            code = "SOUNDPAD_CLOSED"
        else:
            code = "SERVER_ERROR"
        return {"connected": False, "status": "disconnected", "windows": WINDOWS, "error_code": code}

@app.get("/api/sounds")
async def get_sounds():
    data = load_data()
    return data

@app.post("/api/sounds")
async def add_sound(req: AddSoundRequest):
    data = load_data()
    sound_id = f"s_{int(time.time() * 1000)}"
    new_sound = SoundEntry(
        id=sound_id,
        name=req.name,
        soundpad_index=req.soundpad_index,
        category=req.category
    )
    data["sounds"].append(new_sound.model_dump())
    save_data(data)
    return new_sound

@app.post("/api/sounds/batch")
async def batch_add_sounds(sounds_list: list[AddSoundRequest]):
    data = load_data()
    added = []
    existing_indexes = {s["soundpad_index"] for s in data["sounds"]}
    for req in sounds_list:
        if req.soundpad_index in existing_indexes:
            continue
        sound_id = f"s_{int(time.time() * 1000)}_{req.soundpad_index}"
        new_s = SoundEntry(id=sound_id, name=req.name, soundpad_index=req.soundpad_index, category=req.category)
        data["sounds"].append(new_s.model_dump())
        added.append(new_s.model_dump())
        existing_indexes.add(req.soundpad_index)
    save_data(data)
    return {"added": added, "count": len(added)}

@app.patch("/api/sounds/{sound_id}")
async def update_sound(sound_id: str, updates: SoundUpdate):
    data = load_data()
    for sound in data["sounds"]:
        if sound["id"] == sound_id:
            for key, val in updates.model_dump(exclude_none=True).items():
                sound[key] = val
            save_data(data)
            return sound
    raise HTTPException(status_code=404, detail="Sound not found")

@app.delete("/api/sounds/{sound_id}")
async def delete_sound(sound_id: str):
    data = load_data()
    data["sounds"] = [s for s in data["sounds"] if s["id"] != sound_id]
    save_data(data)
    return {"ok": True}

@app.post("/api/play")
async def play_sound(req: PlayRequest):
    data = load_data()
    sound = next((s for s in data["sounds"] if s["id"] == req.sound_id), None)
    if not sound:
        raise HTTPException(status_code=404, detail="Sound not found")
    
    result = sp_play_sound(sound["soundpad_index"])
    
    sound["play_count"] = sound.get("play_count", 0) + 1
    sound["last_played"] = time.time()
    save_data(data)
    
    return {"ok": True, "result": result, "play_count": sound["play_count"]}

@app.post("/api/stop")
async def stop_sound():
    result = sp_stop_sound()
    return {"ok": True, "result": result}

@app.post("/api/mute")
async def mute_sound():
    result = soundpad_call("DoMuteSound()")
    return {"ok": True, "result": result}

@app.get("/api/playstatus")
async def get_play_status():
    try:
        result = sp_get_playback_status()
        playing = "PLAYING" in result.upper() or result.strip() == "1"
        return {"playing": playing, "raw": result}
    except:
        return {"playing": False, "raw": ""}

@app.post("/api/volume")
async def set_volume(req: VolumeRequest):
    data = load_data()
    result = ""
    for cmd in [f"DoSetSoundboardVolume({req.volume})", f"SetSoundboardVolume({req.volume})"]:
        try:
            result = soundpad_call(cmd)
            break
        except:
            pass
    data["settings"]["volume"] = req.volume
    save_data(data)
    return {"ok": True, "result": result}

@app.get("/api/soundpad/list")
async def get_soundpad_list():
    """Fetch sound list directly from Soundpad"""
    result = sp_get_sound_list()
    return {"raw": result}

@app.post("/api/categories")
async def add_category(req: CategoryRequest):
    data = load_data()
    if req.name not in data["categories"]:
        data["categories"].append(req.name)
        save_data(data)
    return data["categories"]

@app.delete("/api/categories/{name}")
async def delete_category(name: str):
    data = load_data()
    if name == "Genel":
        raise HTTPException(status_code=400, detail="Cannot delete default category")
    data["categories"] = [c for c in data["categories"] if c != name]
    for sound in data["sounds"]:
        if sound["category"] == name:
            sound["category"] = "Genel"
    save_data(data)
    return data["categories"]

@app.post("/api/reorder")
async def reorder_sounds(req: ReorderRequest):
    data = load_data()
    sounds_map = {s["id"]: s for s in data["sounds"]}
    data["sounds"] = [sounds_map[sid] for sid in req.sound_ids if sid in sounds_map]
    save_data(data)
    return {"ok": True}

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    filename = f"img_{int(time.time() * 1000)}{ext}"
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(await file.read())
    return {"url": f"/static/images/{filename}"}

@app.post("/api/validate-sounds")
async def validate_sounds():
    """Check which sounds still exist in Soundpad and mark unavailable ones"""
    try:
        raw = sp_get_sound_list()
        import re
        indexes = set(int(m) for m in re.findall(r'index="(\d+)"', raw))
        data = load_data()
        changed = 0
        for sound in data["sounds"]:
            was_unavailable = sound.get("unavailable", False)
            now_unavailable = sound["soundpad_index"] not in indexes
            if was_unavailable != now_unavailable:
                sound["unavailable"] = now_unavailable
                changed += 1
        if changed:
            save_data(data)
        return {"ok": True, "checked": len(data["sounds"]), "changed": changed}
    except Exception as e:
        return {"ok": False, "error": str(e)}

app.mount("/static", StaticFiles(directory=str(_static_root)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index = _static_root / "index.html"
    if index.exists():
        return index.read_text(encoding="utf-8")
    return "<h1>Frontend not found. Place index.html in static/</h1>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7878, reload=False)
