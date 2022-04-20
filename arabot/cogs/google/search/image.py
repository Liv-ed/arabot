import logging
from io import BytesIO
from mimetypes import guess_extension
from pathlib import Path

import disnake
from aiohttp import ClientResponse
from arabot.core import Ara, Category, Cog, Context
from disnake.ext.commands import command


class ImageSearch(Cog, category=Category.LOOKUP, keys={"g_isearch_key", "g_cse"}):
    BASE_URL = "https://www.googleapis.com/customsearch/v1"
    SVG_MIME = "image/svg+xml"

    def __init__(self, ara: Ara):
        self.ara = ara

    @command(aliases=["i", "img"], brief="Top search result from Google Images")
    async def image(self, ctx: Context, *, query):
        async with ctx.typing():
            images = await self.fetch_images(query)
            async for image_file in self.without_svg(images):
                await ctx.send(file=image_file)
                break
            else:
                await ctx.send("No images found")

    async def fetch_images(self, query) -> list:
        data = await self.ara.session.fetch_json(
            self.BASE_URL,
            params={
                "key": self.g_isearch_key,
                "cx": self.g_cse,
                "q": query + " -filetype:svg",
                "searchType": "image",
            },
        )
        return data.get("items", [])

    async def without_svg(self, im: list[dict]) -> disnake.File:
        for item in im:
            if self.SVG_MIME in (item.get("mime"), item.get("fileFormat")):
                continue

            image_url = item["link"]
            try:
                async with self.ara.session.get(image_url) as resp:
                    if not resp.ok or resp.content_type == self.SVG_MIME:
                        continue
                    image = await resp.read()
            except Exception as e:
                logging.error(f"{e}\nFailed image: {image_url}")
            else:
                image = BytesIO(image)
                filename = self.extract_filename(resp)
                yield disnake.File(image, filename)

    @staticmethod
    def extract_filename(response: ClientResponse) -> str:
        fn = Path(
            getattr(response.content_disposition, "filename", response.url.path) or "image"
        ).stem
        ext = guess_extension(response.headers.get("Content-Type", "image/png"), strict=False)

        return fn + ext
