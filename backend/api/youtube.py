from aiohttp import ClientSession
from fastapi import APIRouter
from backend import get_session, mongo
from datetime import datetime, timedelta
from yt_dlp import YoutubeDL
from typing import List
import yt_dlp
import os
import subprocess

from pydantic import BaseModel
from typing import List

class ClipRequest(BaseModel):
    kills: List[List[int]]
    url: str

router = APIRouter(
    tags=["root"],
    responses={404: {"description": "Not found"}},
)

@router.get("/info")
async def get_video_info(url: str):
    check = await mongo.db.summary.find_one({"url": url})
    if check:
        check.pop("_id", None)
        return check, {"type": "cached"}

    async with await get_session() as session:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info, {"type": "fetched"}
            except Exception as e:
                return {"error": str(e)}
                  
def download_sections(*ranges):
    def inner(info_dict, ydl):
        for idx, (start, end) in enumerate(ranges):
            yield {
                'start_time': start,
                'end_time': end,
                'index': idx
            }
    return inner

def download_clips(url, segments, output_template):
    output_files = []

    ydl_opts = {
        "merge_output_format": "mp4",
        "remux_video": "mp4",
        "format": (
            "bestvideo[ext=mp4][vcodec*=avc1][fps=60]+"
            "bestaudio[ext=m4a]/best[ext=mp4][vcodec*=avc1][fps=60]"
        ),
        'outtmpl': output_template, 
        'download_ranges': download_sections(*segments)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        video_id = info_dict['id']
        for i in range(len(segments)):
            # Build file name manually
            output_file = output_template % {
                "title": info_dict['title'],
                "section_number": i,
                "id": video_id,
                "ext": "mp4"
            }
            output_files.append(output_file)

    return output_files

def concat_mp4_files(files: list[str], output_path: str):
    list_file = "concat_list.txt"
    with open(list_file, "w") as f:
        for file in files:
            f.write(f"file '{file}'\n")

    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",               # Lower = better quality (17–23 sweet spot)
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ], check=True)

    # Optionally clean up
    os.remove(list_file)
    for file in files:
        os.remove(file)
        
@router.post("/create-clip")
async def create_clip(body: ClipRequest):
    print(body.kills, body.url)
    kills = body.kills
    url = body.url

    files = download_clips(
        url=url,
        segments=kills,
        output_template="clips/clip_%(section_number)s.%(ext)s"
    )
    # files = ""

    concat_mp4_files(files, datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".mp4")
