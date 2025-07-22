from aiohttp import ClientSession
from fastapi import APIRouter
from backend import get_session, mongo
from datetime import datetime, timedelta
from yt_dlp import YoutubeDL

router = APIRouter(
	tags=["root"],
	responses={404: {"description": "Not found"}},
)

@router.get("/info")
async def get_video_info(url: str):
	check = await mongo.db.summary.find_one({"url": url})
	if check:
		check.pop("_id", None)
		return check["matches"], {"type": "cached"}

	async with await get_session() as session:
		ydl_opts = {
			'format': 'best',
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
