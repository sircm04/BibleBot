import os

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord.ext import menus

from dotenv import load_dotenv

import re

from interfaces import bible_gateway
import search_paginator

BIBLE_BOT_VERSION = 'v0.4'

# Load Discord token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Regex for finding and parsing verses
p = re.compile(r'(?<!\\)(?P<book>Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|(?:1|I|2|II)(?:\s+)?Samuel'
            r'|(?:1|I|II)(?:\s+)?Kings|(?:1|I|2|II)(?:\s+)?Chronicles|Ezra|Nehemiah|Esther|Job|Psalm(?:s)?|Proverbs|Ecclesiastes'
            r'|Song(?:\s+)?of(?:\s+)?(Solomon|Songs)|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah'
            r'|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|Acts|Romans|(?:1|I|2|II)(?:\s+)?Corinthians'
            r'|Galatians|Ephesians|Philippians|Colossians|(?:1|I|2|II)(?:\s+)?Thessalonians|(?:1|I|2|II)(?:\s+)?Timothy|Titus|Philemon|Hebrews'
            r'|James|(?:1|I|2|II)(?:\s+)?Peter|(?:1|I|2|II|3|III)(?:\s+)?John|John|Jude|Revelation|(?:(?:1|I|2|II|3|III)\s+)?[\w]+[.]+)(?:\s+)?'
            r'(?P<chapter>\d+)(?!-)(?::(?P<verse>\d+))?(?:-(?P<endverse>\d+))?(?!:-)(?:(?:\s+)?(?P<version>(?:\w+(?!\|))|(?:\[[\w\|]+\])))?(?!-)(?!:)',
            flags = re.IGNORECASE)

p2 = re.compile(r'(\w+)(?:\|)?', flags = re.IGNORECASE)

DEFAULT_VERSION = 'ESV'

client = commands.Bot(command_prefix = '!', intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands = True)

@client.event
async def on_ready():
    await client.change_presence(activity = discord.Game(name=BIBLE_BOT_VERSION))
    print(f'{ client.user } has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message) and 'hello' in message.content.lower():
        await message.channel.send(f'Hey { message.author.mention }!')

    # Detect and parse verse then return appropriate passage
    for m in re.finditer(p, message.content):
        book = m.group('book').title()
        chapter = m.group('chapter')
        start_verse = m.group('verse')
        end_verse = m.group('endverse')
        version = m.group('version') or DEFAULT_VERSION
        versions = [m2.group(0) for m2 in re.finditer(p2, version)]

        reference = f'{ book } { chapter }'

        if start_verse:
            reference += f':{ start_verse }'
            if end_verse:
                reference += f'-{ end_verse }'

        for ver in versions:
            if not bible_gateway.is_valid_version(ver):
                if len(versions) == 1:
                    ver = DEFAULT_VERSION
                else:
                    break

            verse = bible_gateway.search_verse(reference, ver, True, True)

            if verse is not None:
                if len(verse.text) > 2048:
                    await message.channel.send('That passage was too large to grab, sorry...')
                else:
                    embed = discord.Embed(title = verse.passage, description = verse.text, color = 0x7289da)
                    embed.set_author(name = verse.version)
                    embed.set_footer(text = f'BibleBot { BIBLE_BOT_VERSION }', icon_url = 'https://cdn.discordapp.com/avatars/812508314046562334/4a81c5c4bfb245a225512896745c49e2.webp')
                    await message.channel.send(embed = embed)

    await client.process_commands(message)
    
@slash.slash(name = 'search', description = 'Searches the Bible', guild_ids = [ 842845804451594241 ])
async def search(ctx, version, query):
    await ctx.send('Searching for instances...')
    results = bible_gateway.search(query, version)
    m = menus.MenuPages(source = search_paginator.SearchPaginator(results, query, BIBLE_BOT_VERSION), clear_reactions_after = True)
    await m.start(ctx)

@slash.slash(name = 'setversion', description = 'Sets the preferred bible translation', guild_ids = [ 842845804451594241 ])
async def setversion(ctx, version):
    global DEFAULT_VERSION
    DEFAULT_VERSION = version
    await ctx.send(f'Set default version to { version }!')


@slash.slash(name = 'ping', description = 'Checks the latency', guild_ids = [ 842845804451594241 ])
async def ping(ctx):
    await ctx.send(f'Pong! { round(client.latency * 1000) }ms ')

client.run(TOKEN)