from aiohttp import ClientSession
from arabot.core import Category, Cog, Context
from disnake.ext.commands import command


class Youtube(Cog, category=Category.LOOKUP, keys={"g_yt_key"}):
    YT_BASE_URL = "https://www.googleapis.com/youtube/v3/search"

    def __init__(self, session: ClientSession):
        self.session = session

    @command(aliases=["yt"], brief="Top search result from YouTube")
    async def youtube(self, ctx: Context, *, query):
        data = await self.session.fetch_json(
            self.YT_BASE_URL,
            params={
                "key": self.g_yt_key,
                "q": query,
                "maxResults": 1,
                "type": "video",
                "regionCode": "US",
            },
        )
        await ctx.reply(
            "https://youtu.be/" + data["items"][0]["id"]["videoId"]
            if data.get("items")
            else "No videos found"
        )