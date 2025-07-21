from aiohttp import ClientSession
from fastapi import APIRouter
from backend import get_session, mongo
from datetime import datetime, timedelta

router = APIRouter(
	tags=["root"],
	responses={404: {"description": "Not found"}},
)

async def fetch_account_data(name: str, tag: str):
	account = await mongo.db.accounts.find_one({"name": name, "tag": tag})
	if account and "expires_at" in account and account["expires_at"] > datetime.now():
		return {"data": account}

	async with await get_session() as session:
		url = f"https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}"
		async with session.get(url) as response:
			if response.status == 200:
				data = await response.json()

				puuid = data.get("data", {}).get("puuid")
				data["expires_at"] = datetime.now() + timedelta(days=1) # card updates and stuff
				await mongo.db.accounts.update_one(
					{"puuid": puuid},
					{"$set": data.get("data", {})},
					upsert=True
				)

				return data
			else:
				return {"error": "Account not found"}
		
async def fetch_matches_data(name: str, tag: str, region: str, platform: str, page: int = 1):
	async with await get_session() as session:
		url = f"https://api.henrikdev.xyz/valorant/v4/matches/{region}/{platform}/{name}/{tag}?size=10&start={(page - 1) * 10}"
		print(url)
		async with session.get(url) as response:
			if response.status == 200:
				data = await response.json()
				return data
			else:
				return {"error": "Matches not found"}, response.status

@router.get("")
async def get_account(name: str, tag: str):
	return await fetch_account_data(name, tag)

@router.get("/matches")
async def get_matches(name: str, tag: str, page: int = 1):
	account = await fetch_account_data(name, tag)

	if "error" in account:
		return account

	data = account.get("data", {})
	region = data.get("region", "na")
	platform = "pc"                        # valorant console is not real.

	matchlist = await fetch_matches_data(name, tag, region, platform, page)
	
	# clean data, only keep metadata and playerlist
	matches = []
	for _match in matchlist.get("data", []):
		up_data = _match.get("metadata")

		up_data.pop("party_rr_penaltys")

		up_data["playerlist"] = [
			player["puuid"] for player in _match["players"]
		]

		await mongo.db.matches.update_one(
			{"match_id": up_data["match_id"]},
			{"$set": up_data},
			upsert=True
		)

		matches.append(up_data)

	return {
		"data": matches,
		"page": page,
		"total": len(matches),
	}