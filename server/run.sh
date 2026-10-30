#!/data/data/com.termux/files/usr/bin/bash
# usage: API_KEY=yoursecret bash run.sh
cd "$(dirname "$0")"
termux-wake-lock
pip install -q -U "yt-dlp[default]"        # keep yt-dlp fresh on every start
uvicorn server:app --host 127.0.0.1 --port 8000 &
cloudflared tunnel --url http://127.0.0.1:8000   # prints the https://....trycloudflare.com address
