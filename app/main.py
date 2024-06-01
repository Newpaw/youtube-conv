from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from yt_dlp import YoutubeDL
import os
import uuid



app = FastAPI()

# Nastavení cesty pro ukládání souborů z environmentální proměnné
DOWNLOAD_DIRECTORY = os.getenv("DOWNLOAD_DIRECTORY", "downloads")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/downloads", StaticFiles(directory=DOWNLOAD_DIRECTORY), name="downloads")

# Funkce ke stažení audia z dané URL pomocí yt-dlp
def download_audio(yt_url: str) -> str:
    unique_id = str(uuid.uuid4())
    output_dir = os.path.join(DOWNLOAD_DIRECTORY, unique_id)
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s')
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(yt_url, download=True)
        filename = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        return filename

@app.post("/download/")
async def download_file(url: str = Form(...)):
    try:
        filename = download_audio(url)
        file_url = "/" + filename.replace("\\", "/")
        return JSONResponse(content={"file_url": file_url})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Static route for frontend
@app.get("/")
async def main():
    return FileResponse("app/static/index.html")
