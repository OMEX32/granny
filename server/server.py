import os, re, glob, shutil, tempfile, subprocess
from urllib.parse import urlparse
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import yt_dlp

KEY = os.environ.get("API_KEY", "")
ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")   # set to your Vercel URL later
MAX_LEN = 20 * 60                                  # refuse videos longer than 20 min
OPTS = {"quiet": True, "noplaylist": True, "js_runtimes": {"node": {}}}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[ORIGIN], allow_methods=["GET"], allow_headers=["X-Key"])

def check(key, url):
    if not KEY or key != KEY:
        raise HTTPException(401)
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not re.fullmatch(r"((www|m|music)\.)?(youtube\.com|youtu\.be)", (p.hostname or "").lower()):
        raise HTTPException(400)

def lookup(url):
    try:
        with yt_dlp.YoutubeDL(OPTS) as y:
            d = y.extract_info(url, download=False)
    except Exception:
        raise HTTPException(502)
    if not d.get("duration") or d["duration"] > MAX_LEN:
        raise HTTPException(400)
    return d

@app.get("/info")
def info(url: str, x_key: str = Header(None)):
    check(x_key, url)
    d = lookup(url)
    return {"title": d.get("title", ""), "duration": int(d["duration"])}

@app.get("/clip")
def clip(url: str, start: int = Query(0, ge=0), dur: int = Query(30, ge=1, le=300), x_key: str = Header(None)):
    check(x_key, url)
    lookup(url)
    tmp = tempfile.mkdtemp()
    try:
        with yt_dlp.YoutubeDL({**OPTS, "format": "bestaudio/best", "outtmpl": tmp + "/a.%(ext)s"}) as y:
            y.download([url])
        src = glob.glob(tmp + "/a.*")[0]
        out = tmp + "/clip.m4a"
        subprocess.run(["ffmpeg", "-y", "-ss", str(start), "-t", str(dur), "-i", src, "-vn",
                        "-c:a", "aac", "-b:a", "192k", out], check=True, capture_output=True, timeout=180)
    except Exception:
        shutil.rmtree(tmp, True)
        raise HTTPException(502)
    return FileResponse(out, media_type="audio/mp4", background=BackgroundTask(shutil.rmtree, tmp, True))
