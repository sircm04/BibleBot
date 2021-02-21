import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

import re

from interfaces import bible_gateway
from utils import text_purification

# Load Discord token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = '!')

# Regex for finding and parsing verses
p = re.compile(r'(?<!\\)(?P<book>Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges'
            r'|Ruth|(?:1|I|2|II)(?:\s+)?Samuel|(?:1|I|II)(?:\s+)?Kings|(?:1|I|2|II)(?:\s+)?Chronicles'
            r'|Ezra|Nehemiah|Esther|Job|Psalm|Proverbs|Ecclesiastes|Song(?:\s+)?of(?:\s+)?Solomon|Isaiah'
            r'|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah'
            r'|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|Acts'
            r'|Romans|(?:1|I|2|II)(?:\s+)?Corinthians|Galatians|Ephesians|Philippians'
            r'|Colossians|(?:1|I|2|II)(?:\s+)?Thessalonians|(?:1|I|2|II)(?:\s+)?Timothy|Titus|Philemon'
            r'|Hebrews|James|(?:1|I|2|II)(?:\s+)?Peter|(?:1|I|2|II|3|III)(?:\s+)?John|John|Jude|Revelation)'
            r'(?:\s+)(?P<chapter>\d+)(?!-)(?::(?P<verse>\d+))?(?:-(?P<endverse>\d+))?(?!:-)(?:\s+(?P<version>\w+))?(?!-)(?!:)',
            flags = re.IGNORECASE)

DEFAULT_VERSION = 'ESV'

@client.event
async def on_ready():
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
        verse = m.group('verse')
        end_verse = m.group('endverse')
        version = m.group('version') or DEFAULT_VERSION
        
        raw_verse = f"{ book } { chapter }"

        if verse:
            raw_verse += f":{ verse }"
        if end_verse:
            raw_verse += f"-{ end_verse }"
        
        passage = ''
        response = bible_gateway.search(raw_verse, version, DEFAULT_VERSION)

        if response is not None:
            for i, key in enumerate(response[0]):
                passage += (' ' if (i > 0) else '') + ('<**' + key + '**> ' + text_purification.purify_verse_text(response[0][key]))
        
            if len(passage) > 2048:
                await message.channel.send('That passage was too large to grab, sorry...')
            else:
                embed = discord.Embed(title = f'{ response[1] } - { response[2] }', description = f'{ passage }', color = 0x6662E2)
                embed.set_footer(text = 'PythonBot v0.1', icon_url = 'https://discord.com/assets/6debd47ed13483642cf09e832ed0bc1b.png')
                await message.channel.send(embed = embed)

    await client.process_commands(message)

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! { round(client.latency * 1000) }ms ')

@client.command()
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit = amount)

client.run(TOKEN)