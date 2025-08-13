from fastapi import APIRouter, UploadFile, File, HTTPException
import os, uuid
from app.services.model_inference import transcribe_audio, synthesize_text

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    tmp_dir = "/tmp/custom_voicebot"
    os.makedirs(tmp_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(tmp_dir, filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    text = transcribe_audio(path)
    return {"transcript": text}

@router.post("/speak")
def speak(text: str):
    audio_bytes = synthesize_text(text)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="TTS not configured")
    return {"audio_base64": audio_bytes.hex()}
