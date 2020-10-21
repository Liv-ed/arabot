from discord.ext.commands import Cog
from re import search
from .._utils import text_reaction

class Urban(Cog, name="Eggs"):
	def __init__(self, client):
		self.bot = client

	@text_reaction(send=False, regex=r"^(?:wh?[ao]t(?:['’]?s|\sis)\s)((?:(?!up|good|with|it|this|that|so|the|about|goin|happenin).)*?)\??$", check=lambda msg: len(msg.content) < 30)
	async def urban_listener(self, msg):
		term = search(r"^(?:wh?[ao]t(?:['’]?s|\sis)\s)((?:(?!up|good|with|it|this|that|so|the|about|goin|happenin).)*?)\??$", msg.content.lower()).group(1)
		await self.bot.get_command("urban")(await self.bot.get_context(msg), term=term)

def setup(client):
	client.add_cog(Urban(client))