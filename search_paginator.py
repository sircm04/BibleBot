import discord
from discord.ext import menus

from interfaces import bible_gateway

class SearchPaginator(menus.ListPageSource):
    def __init__(self, data, query, BIBLE_BOT_VERSION):
        self.query = query
        self.BIBLE_BOT_VERSION = BIBLE_BOT_VERSION
        super().__init__(data, per_page = 5)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(title = f'Search results for \'{ " ".join(self.query) }\'', description = f'**Page { menu.current_page + 1 } of { self.get_max_pages() }**', color = 0x7289da)
        for i, v in enumerate(entries, start = offset):
            embed.add_field(name = v[0], value = v[1])
        embed.set_footer(text = f'BibleBot { self.BIBLE_BOT_VERSION }', icon_url = 'https://cdn.discordapp.com/avatars/812508314046562334/4a81c5c4bfb245a225512896745c49e2.webp')
        return embed