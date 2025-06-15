import discord
from discord import SelectOption, Button # import Select, SelectOption, Button
from discord.ext import commands
import asyncio
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
import re
import json
import os
from yt_dlp import YoutubeDL

from nudge_bot.utils.logger import configure_logger
import logging

logger = logging.getLogger(__name__)
configure_logger(logger)

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = {}
        self.is_paused = {}
        self.musicQueue = {}
        self.queueIndex = {}

        self.YTDL_OPTIONS = {
            'format': 'bestaudio/best', 
            'extractaudio': True,
            'noplaylist': True,
            'keepvideo': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }]
        }
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }

        self.embedBlue = 0x2c76dd
        self.embedRed = 0xdf1141
        self.embedGreen = 0x0eaa51
        
        self.vc = {}

    async def cog_load(self): # called when cog is loaded: like on_ready
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.musicQueue[id] = []
            self.queueIndex[id] = 0
            self.vc[id] = None
            self.is_paused[id] = self.is_playing[id] = False

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = int(member.guild.id)
        if member.id != self.bot.user.id and before.channel != None and after.channel != before.channel:
            remainingChannelMembers = before.channel.members
            if len(remainingChannelMembers) == 1 and remainingChannelMembers[0].id == self.bot.user.id and self.vc[id].is_connected():
                self.is_playing[id] = self.is_paused[id] = False
                self.musicQueue[id] = []
                self.queueIndex[id] = 0
                logger.info("Disconnected because voice channel is empty.")
                await self.vc[id].disconnect()

    def now_playing_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.author
        avatar = author.avatar.url

        embed = discord.Embed(
            title = "Now laying",
            description=f'[{title}]({link})',
            colour = self.embedBlue
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed

    async def join_VC(self, ctx, channel):
        id = int(ctx.guild.id)
        logger.info("Joining voice channel...")
        if self.vc[id] == None or not self.vc[id].is_connected():
            self.vc[id] = await channel.connect()
            logger.info("Successfully joined voice channel.")
            
            if self.vc[id] == None:
                await ctx.send("Could not connect to the voice channel")
                logger.warning("Could not connect to the voice channel")
                return
        else:
            await self.vc[id].move_to(channel)
            logger.info("Successfully switched voice channels.")

    def search_YT(self, search):
        logger.info("Searching YouTube...")
        queryString = parse.urlencode({'search_query': search})
        htmContent = request.urlopen(
            'http://www.youtube.com/results?' + queryString
        )
        searchResults = re.findall('/watch\?v=(.{11})', htmContent.read().decode())
        return searchResults[0:10]
    
    def extract_YT(self, url):
        logger.info("Extracting info from YouTube...")
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                logger.info("Successfully extracted from YouTube.")
            except:
                logger.warning("Failed to extract from YouTube.")
                return False
        return {
            'link': 'https://www.youtube.com/watch?v=' + url,
            'thumbnail': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
            'source': info['url'],
            'title': info['title']
        }       
    
    def play_next(self, ctx):
        logger.info("Received request to play next song in queue...")
        id = int(ctx.guild.id)
        if not self.is_playing[id]:
            logger.warning("Bot is not playing music.")
            return
        if self.queueIndex[id] + 1 < len(self.musicQueue[id]):
            logger.info("Playing next song in queue...")
            self.is_playing[id] = True
            self.queueIndex[id] += 1

            song = self.musicQueue[id][self.queueIndex[id]][0]
            message = self.now_playing_embed(ctx, song)
            coroutine = ctx.send(embed=message)
            logger.info("Sent embed.")
            future = run_coroutine_threadsafe(coroutine, self.bot.loop)
            try:
                future.result()
            except:
                pass

            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            logger.info("Playing music.")
        else:
            logger.info("Reached end of queue.")
            self.queueIndex[id] += 1
            self.is_playing[id] = False    

    async def play_music(self, ctx):
        id = int(ctx.guild.id)
        if self.queueIndex[id] < len(self.musicQueue[id]):
            self.is_playing[id] = True
            self.is_paused[id] = False

            await self.join_VC(ctx, self.musicQueue[id][self.queueIndex[id]][1])

            song = self.musicQueue[id][self.queueIndex[id]][0]
            message = self.now_playing_embed(ctx, song)
            await ctx.send(embed=message)
            logger.info("Sent embed.")

            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            logger.info("Playing music.")
        else:
            await ctx.send("No songs in queue.")
            logger.warning("No songs in queue.")
            self.queueIndex[id] += 1
            self.is_playing = False

    @commands.command(
        name="play",
        aliases=["p"],
        help=""
    )
    async def play(self, ctx, *args):
        logger.info("Received \".play\" command.")
        search = " ".join(args)
        id = int(ctx.guild.id)
        try:
            userChannel = ctx.author.voice.channel
        except:
            logger.error("You must be connected to a voice channel.")
            await ctx.send("You must be connected to a voice channel.")
            return
        if not args:
            if len(self.musicQueue[id]) == 0:
                await ctx.send("There are no songs to be played in the queue.")
                logger.warning("There are no songs to be played in the queue.")
                return
            elif not self.is_playing[id]:
                if self.musicQueue[id] == None or self.vc[id] == None:
                    logger.info("Starting queue...")
                    await self.play_music(ctx)
                else:
                    logger.info("Resuming music...")
                    self.is_paused[id] = False
                    self.is_playing[id] = True
                    self.vc[id].resume()
            else:
                logger.warning("Already playing.")
                return
        else:
            song = self.extract_YT(self.search_YT(search)[0])
            if type(song) == type(True):
                await ctx.send("Could not download song. Incorrect format, try different keywords.")
                logger.error("Could not download song. Incorrect format, try different keywords.")
            else:
                self.musicQueue[id].append([song, userChannel])

                if not self.is_playing[id]:
                    await self.play_music(ctx)
                else:
                    message = "Added to queue"
                    await ctx.send(message)
                    logger.info("Added to queue.")

    @commands.command(
        name="join",
        aliases=["j"],
        help=""
    )
    async def join(self, ctx):
        if ctx.author.voice:
            userChannel = ctx.author.voice.channel
            await self.join_VC(ctx, userChannel)
            await ctx.send(f'NudgeBot has joined {userChannel}')
        else:
            await ctx.send("You must be connected to a voice channel.")

    @commands.command(
        name="leave",
        aliases=["l"],
        help=""
    )
    async def leave(self, ctx):
        id = int(ctx.guild.id)
        self.is_playing[id] = self.is_paused[id] = False
        self.musicQueue[id] = []
        self.queueIndex[id] = 0
        if self.vc[id] != None:
            await ctx.send("NudgeBot has left the chat.")
            await self.vc[id].disconnect()

async def setup(bot):
    await bot.add_cog(MusicCog(bot))