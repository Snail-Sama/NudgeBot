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

class MusicDropdown(discord.ui.Select):
    def __init__(self, cog, ctx, selectOptions):
        self.cog = cog
        self.ctx = ctx
        options=selectOptions

        super().__init__(placeholder="Select an option", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        logger.info("Dropdown callback.")
        await self.cog.selection_submit(ctx=self.ctx, song=self.values[0])
        interaction.response.is_done()

class MusicView(discord.ui.View):
    def __init__(self, cog, ctx, selectOptions):
        super().__init__()
        self.add_item(MusicDropdown(cog=cog, ctx=ctx, selectOptions=selectOptions))
    

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
            title = "Now Playing",
            description=f'[{title}]({link})',
            colour = self.embedBlue
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed
    
    def added_song_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.author
        avatar = author.avatar.url

        embed = discord.Embed(
            title = "Song Added to Queue!",
            description=f'[{title}]({link})',
            colour = self.embedRed
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
    
    def get_YT_title(self, videoID):
        params = {
            "format": "json", 
            "url": "https://www.youtube.com/watch?v=%s" % videoID
        }
        url = "https://www.youtube.com/oembed"
        query_string = parse.urlencode(params)
        url = url + "?" + query_string
        with request.urlopen(url) as response:
            responseText = response.read()
            data = json.loads(responseText.decode())
            return data['title']

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
                    message = self.added_song_embed(ctx, song)
                    await ctx.send(embed=message)
                    logger.info("Added to queue.")

    @commands.command(
        name="add",
        aliases=["a"],
        help=""
    )
    async def add(self, ctx, *args):
        logger.info("Received request to add a song to the queue.")
        search = " ".join(args)
        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("You must be in a voice channel.")
            logger.warning("You must be in a voice channel.")
            return
        if not args:
            await ctx.send("You need to specify a song to be added.")
            logger.warning("You need to specify a song to be added.")
        else:
            song = self.extract_YT(self.search_YT(search)[0])
            if type(song) == type(False):
                await ctx.send("Could not download the song. Incorrect format, try different keywords.")
                logger.error("Could not download the song.")
                return
            else:
                self.musicQueue[ctx.guild.id].append([song, userChannel])
                message = self.added_song_embed(ctx, song)
                await ctx.send(embed=message)
                logger.info("Added to queue.")

    @commands.command(
        name="search",
        aliases=["find", "sr"],
        help=""
    )
    async def search(self, ctx, *args):
        search = " ".join(args)
        songNames = []
        selectionOptions = []
        embedText = ""

        if not args:
            await ctx.send("You must specify search terms to use this command.")
            logger.error("No search terms supplied.")
            return
        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("You must be in a voice channel.")
            logger.error("Not in a voice channel")
            return
        
        await ctx.send("Fetching search results...")
        logger.info("Fetching search resutls...")

        songTokens = list(set(self.search_YT(search))) # come back to this and still get top ten results without duplicates

        for i, token in enumerate(songTokens):
            url = "https://www.youtube.com/watch?v=" + token
            name = self.get_YT_title(token)
            songNames.append(name)
            embedText += f"{i+1} - [{name}]({url})\n"

        for i, title, token in zip(range(10), enumerate(songNames), enumerate(songTokens)):
            selectionOptions.append(SelectOption(
                label=f"{i+1} - {title[1][:100]}", value="https://www.youtube.com/watch?v=" + token[1]))
            
        searchResults = discord.Embed(
            title="Search Results",
            description=embedText,
            colour=self.embedRed
        )
        
        message = await ctx.send(embed=searchResults, view=MusicView(cog=self, ctx=ctx, selectOptions=selectionOptions))
        logger.info("here")

    async def selection_submit(self, ctx, song):
        songRef = self.extract_YT(song)
        if type(songRef) == type(True):
            await ctx.send("Could not download the song. Incorrect format, try different keywords.")
            logger.error("Could not download the song. Incorrect format, try different keywords.")
            return
        embedResponse = discord.Embed(
            title=f"{songRef["title"]} Selected",
            description=f"[{songRef["title"]}]({songRef["link"]}) added to the queue!",
            colour=self.embedRed
        )
        embedResponse.set_thumbnail(url=songRef["thumbnail"])
        # await message.delete()
        await ctx.send(embed=embedResponse)
        userChannel = ctx.author.voice.channel
        self.musicQueue[ctx.guild.id].append([songRef, userChannel])


    @commands.command(
        name="pause",
        aliases=["stop", "pa"],
        help=""
    )
    async def pause(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("There is no audio to be paused at the moment.")
            logger.warning("There is no audio to be paused at the moment.")
        elif self.is_playing[id]:
            await ctx.send("Audio paused!")
            logger.info("Audio paused!")
            self.is_playing[id] = False
            self.is_paused[id] = True
            self.vc[id].pause()
        elif self.is_paused[id]:
            logger.warning("Already paused.")

    @commands.command(
        name="resume",
        aliases=["re"],
        help=""
    )
    async def resume(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("There is no audio to be played at the moment.")
            logger.warning("There is no audio to be played at the moment.")
        elif self.is_paused[id]:
            await ctx.send("The audio is now playing!")
            logger.info("The audio is now playing!")
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].resume()
        elif self.is_playing[id]:
            logger.warning("Already playing.")

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
            logger.info(f'NudgeBot has joined {userChannel}')
        else:
            await ctx.send("You must be connected to a voice channel.")
            logger.warning("You must be connected to a voice channel.")

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
            logger.info("NudgeBot has left the chat.")
            await self.vc[id].disconnect()
            self.vc[id] = None

async def setup(bot):
    await bot.add_cog(MusicCog(bot))