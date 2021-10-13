import re
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from gtts import gTTS
from wordfreq import zipf_frequency

app = FastAPI()
app.mount("/f", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse("static/index.html")

@app.get("/tts/{lang}/{q}.mp3", summary="gTTS API", response_class=StreamingResponse, responses={
    200: {"content": {"audio/mpeg": {}}}
})
async def tts(q: str, lang: str):
    return make_tts(q, lang)


@app.get("/api/tts", summary="gTTS API", response_class=StreamingResponse, responses={
    200: {"content": {"audio/mpeg": {}}}
})
async def api_tts(q: str, lang: str):
    return make_tts(q, lang)


def make_tts(q: str, lang: str):
    safe_q = re.sub(r"\W+", q, " ")
    cache_path = "static"
    save_path = Path(cache_path, lang, safe_q + ".mp3")

    if not save_path.exists():
        Path(cache_path, lang).mkdir(exist_ok=True)
        gTTS(q, lang=lang).save(str(save_path))

    def iter_file():
        with save_path.open("rb") as f:
            yield from f

    return StreamingResponse(iter_file(), media_type="audio/mpeg")


@app.get("/api/wordfreq", summary="GET Python wordfreq", response_model=Dict[str, float])
async def api_wordfreq(q: str, lang: str, wordlist: str = "best"):
    return make_wordfreq(q.split(","), lang, wordlist)


@app.post("/api/wordfreq", summary="POST Python wordfreq", response_model=Dict[str, float])
async def api_wordfreq_post(lang: str, wordlist: str = "best", q: list[str] = Body(..., embed=True)):
    return make_wordfreq(q, lang, wordlist)


def make_wordfreq(q: list[str], lang: str, wordlist: str = "best"):
    out: Dict[str, float] = {}
    for v in q:
        out[v] = zipf_frequency(v.strip(), lang=lang, wordlist=wordlist)

    return out
