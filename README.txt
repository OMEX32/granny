MIJN FILMPJE

Two parts:
 1. The web app (everything except server/) -> hosted on Vercel.
 2. server/ -> runs on your Android phone in Termux. It downloads the YouTube audio.

A) Phone (Termux)
   pkg install git python ffmpeg nodejs cloudflared
   git clone <your GitHub repo>  &&  cd <repo>/server
   pip install -r requirements.txt
   API_KEY=choose-a-long-secret bash run.sh
   -> look for the https://....trycloudflare.com address in the output.

B) Web app
   Edit config.js: put that address in API_URL and the same secret in API_KEY.
   Push the repo to GitHub, import it on vercel.com (no build settings needed).
   Open the Vercel link on grandma's phone -> "Add to Home Screen".

Notes
 - The trycloudflare address changes every time the tunnel restarts; then update config.js and push.
 - The key in config.js is visible to anyone who opens the site; it only keeps strangers from stumbling on the server.
 - Language: change LANG at the top of the script in index.html ('ar' = Iraqi Arabic, 'nl' or 'en').
