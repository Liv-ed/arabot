from json import loads
from urllib.parse import quote

from arabot.core import Ara, Category, Cog, Context
from arabot.utils import dsafe
from disnake import Embed
from disnake.ext.commands import command


class Wolfram(Cog, category=Category.LOOKUP, keys={"wolfram_id"}):
    def __init__(self, ara: Ara):
        self.ara = ara

    @command(brief="Answer a question")
    async def calc(self, ctx: Context, *, query: str):
        await ctx.trigger_typing()
        query = query.strip("`")
        async with self.ara.session.get(
            "https://api.wolframalpha.com/v2/query",
            params={
                "input": query,
                "format": "plaintext",
                "output": "json",
                "appid": self.wolfram_id,
                "units": "metric",
            },
        ) as wa:
            wa = loads(await wa.text())["queryresult"]
        embed = Embed(
            color=0xF4684C,
            title=dsafe(query),
            url="https://www.wolframalpha.com/input/?i=" + quote(query, safe=""),
        ).set_footer(
            icon_url="https://cdn.iconscout.com/icon/free/png-512/wolfram-alpha-2-569293.png",
            text="Wolfram|Alpha",
        )
        if wa["success"]:
            if "warnings" in wa:
                embed.description = wa["warnings"]["text"]
            for pod in wa["pods"]:
                if pod["id"] == "Recognized input":
                    embed.add_field(
                        name="Input",
                        value=f"[{dsafe(pod['subpods'][0]['plaintext'])}]"
                        f"(https://www.wolframalpha.com/input/?i={quote(pod['subpods'][0]['plaintext'], safe='')})",
                    )
                if "primary" in pod:
                    embed.add_field(
                        name="Result",
                        value="\n".join(dsafe(subpod["plaintext"]) for subpod in pod["subpods"]),
                        inline=False,
                    )
                    break
        elif "tips" in wa:
            embed.description = wa["tips"]["text"]
        await ctx.send(embed=embed)


def setup(ara: Ara):
    ara.add_cog(Wolfram(ara))