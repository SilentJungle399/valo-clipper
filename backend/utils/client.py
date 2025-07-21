import os
from aiohttp import ClientSession

async def get_session():
	"""Create an aiohttp ClientSession with authorization header."""
	return ClientSession(
		headers = {
			"Authorization": os.environ.get("HENRIKDEV_API_KEY", "")
		}
	)