from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from yt_dlp import YoutubeDL
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Funkce ke stažení audia z dané URL pomocí yt-dlp
def download_audio(yt_url: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s'
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(yt_url, download=True)
        filename = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        return filename

@app.post("/download/")
async def download_file(url: str = Form(...)):
    try:
        filename = download_audio(url)
        return FileResponse(path=filename, filename=os.path.basename(filename), media_type='audio/mpeg')
    except Exception as e:
        return {"error": str(e)}

# Static route for frontend
@app.get("/")
async def main():
    return FileResponse("app/static/index.html")
