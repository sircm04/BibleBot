import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

import re

from interfaces import bible_gateway

# Load Discord token from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Regex for finding and parsing verses
p = re.compile(r'(?<!\\)(?P<book>Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|(?:1|I|2|II)(?:\s+)?Samuel'
            r'|(?:1|I|II)(?:\s+)?Kings|(?:1|I|2|II)(?:\s+)?Chronicles|Ezra|Nehemiah|Esther|Job|Psalm|Proverbs|Ecclesiaste'
            r'|Song(?:\s+)?of(?:\s+)?(Solomon|Songs)|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah'
            r'|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|Acts|Romans|(?:1|I|2|II)(?:\s+)?Corinthians'
            r'|Galatians|Ephesians|Philippians|Colossians|(?:1|I|2|II)(?:\s+)?Thessalonians|(?:1|I|2|II)(?:\s+)?Timothy|Titus|Philemon|Hebrews'
            r'|James|(?:1|I|2|II)(?:\s+)?Peter|(?:1|I|2|II|3|III)(?:\s+)?John|John|Jude|Revelation|(?:(?:1|I|2|II|3|III)\s+)?[\w]+[.]+)(?:\s+)?'
            r'(?P<chapter>\d+)(?!-)(?::(?P<verse>\d+))?(?:-(?P<endverse>\d+))?(?!:-)(?:\s+(?P<version>\w+))?(?!-)(?!:)',
            flags = re.IGNORECASE)

DEFAULT_VERSION = 'ESV'

client = commands.Bot(command_prefix = '!')

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
        start_verse = m.group('verse')
        end_verse = m.group('endverse')
        version = m.group('version') or DEFAULT_VERSION
        
        reference = f'{ book } { chapter }'

        if start_verse:
            reference += f':{ start_verse }'
            if end_verse:
                reference += f'-{ end_verse }'

        verse = bible_gateway.search(reference, version, False)
        
        if verse is not None:
            if len(verse.text) > 2048:
                await message.channel.send('That passage was too large to grab, sorry...')
            else:
                embed = discord.Embed(title = verse.title, description = verse.text, color = 0x6662E2)
                embed.set_author(name = f'{ verse.passage } - { verse.version }')
                embed.set_footer(text = 'BibleBot v0.2', icon_url = 'https://discord.com/assets/6debd47ed13483642cf09e832ed0bc1b.png')
                await message.channel.send(embed = embed)

    await client.process_commands(message)

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! { round(client.latency * 1000) }ms ')

@client.command()
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit = amount)

client.run(TOKEN)