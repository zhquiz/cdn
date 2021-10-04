import re
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from gtts import gTTS

app = FastAPI()

@app.get("/api/tts")
def api_tts(q: str, lang: str):
    safe_q = re.sub(r"\W+", q, " ")
    print(Path.cwd())
    save_path = Path("public", lang, safe_q + ".mp3")

    if not save_path.exists():
        Path("public", lang).mkdir(exist_ok=True)
        gTTS(q, lang=lang).save(str(save_path))

    def iter_file():
        with save_path.open("rb") as f:
            yield from f

    return StreamingResponse(iter_file(), media_type="audio/mp3")
