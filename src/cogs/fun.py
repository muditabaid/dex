import discord
import aiohttp
import os
from typing import Optional
from datetime import datetime
from discord.ext import commands
from gtts import gTTS


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ----------------------------------------------------------------------------------------------------------------------

    async def get_iquote(self):
        API_URL = "https://zenquotes.io/api//random"
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as resp:
                quote_json = await resp.json()
                return (quote_json)

    @commands.command(name="inspire", aliases=["iquote"], help="sends a random inspirational quote")
    async def inspire_command(self, ctx):
        embed = discord.Embed(title="Inspirational Quote",
                              colour=ctx.author.colour,
                              timestamp=datetime.utcnow())
        iquote = await self.get_iquote()
        embed.add_field(name="Quote", value=iquote[0]['q'], inline=False)
        embed.add_field(name="Author", value=iquote[0]['a'], inline=False)
        await ctx.send(reference=ctx.message, embed=embed)
    # ----------------------------------------------------------------------------------------------------------------------

    async def get_nasa(self):
        API_URL = "https://api.nasa.gov/planetary/apod?api_key=" + \
            str(os.getenv('DEX_NASA_API_KEY'))
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as resp:
                data_json = await resp.json()
                return (data_json)

    @commands.command(name="apod", aliases=["napod", "astropic", "astropicotd"], help="sends astronomy pic of the day from NASA")
    async def apod_command(self, ctx):
        embed = discord.Embed(title="NASA",
                              description="Picture of the day",
                              colour=0x0B3D91,
                              timestamp=datetime.utcnow())
        embed.set_thumbnail(
            url="https://user-images.githubusercontent.com/63065397/156291255-4af80382-836c-4801-8b4f-47da33ea36c5.png")
        embed.set_footer(text="updated daily at 05:00:00 UTC [00:00:00 ET]")
        nasa_api = await self.get_nasa()
        embed.set_image(url=nasa_api["url"])
        embed.add_field(name="Date", value=nasa_api["date"], inline=False)
        embed.add_field(name="Image Title",
                        value=nasa_api["title"], inline=False)
        await ctx.send(reference=ctx.message, embed=embed)
    # ----------------------------------------------------------------------------------------------------------------------

    async def get_meme(self):
        API_URL = "https://meme-api.herokuapp.com/gimme"
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as resp:
                data_json = await resp.json()
                return (data_json)

    @commands.command(name="meme", aliases=["hehe"], help="sends a random meme")
    async def meme_command(self, ctx):
        embed = discord.Embed(title="MEME",
                              colour=0xffee00,
                              timestamp=datetime.utcnow())
        meme = await self.get_meme()
        embed.add_field(name="Post Link", value=meme["postLink"], inline=True)
        embed.add_field(name="Author", value=meme["author"], inline=True)
        embed.add_field(name="Header", value=meme["title"], inline=False)
        embed.set_image(url=meme["url"])
        embed.set_thumbnail(
            url="https://user-images.githubusercontent.com/63065397/156142184-0675cfee-2863-41d7-bef8-87f600a713b0.png")
        await ctx.send(reference=ctx.message, embed=embed)
    # ----------------------------------------------------------------------------------------------------------------------

    async def get_subreddit(self, subreddit):
        API_URL = str("https://www.reddit.com/r/" + subreddit + ".json")
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as resp:
                data_json = await resp.json()
                return (data_json)

    @commands.command(name="reddit", aliases=["subreddit"], help="shows top headlines of the given subreddit")
    async def reddit_command(self, ctx, subreddit, number: Optional[int]):
        data = await self.get_subreddit(subreddit)
        if ('message' in data.keys()):
            if data['message'] == "Not Found":
                embed = discord.Embed(
                    title="Status",
                    colour=0xff0000,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Error", value="Not Found", inline=True)
                embed.set_footer(text="given subreddit: "+subreddit)
                await ctx.send(reference=ctx.message, embed=embed)
                return
            embed = discord.Embed(
                title="Error",
                description="API Request Fail",
                colour=0xff0000,
                timestamp=datetime.utcnow()
            )
            for key_i in data.keys():
                if key_i != 'message' and key_i != 'error':
                    new_key = key_i
            embed.add_field(name='Error Code', value=str(
                data['error']), inline=True)
            embed.add_field(name='Error Message', value=str(
                data['message']), inline=True)
            if new_key is not None:
                embed.add_field(name=new_key.title(), value=str(
                    data[new_key]), inline=True)
            embed.set_footer(text="given subreddit: "+subreddit)
            await ctx.send(reference=ctx.message, embed=embed)
        else:
            embed = discord.Embed(title=str("/r/"+subreddit),
                                  colour=0xff5700, timestamp=datetime.utcnow())
            embed.set_thumbnail(
                url="https://user-images.githubusercontent.com/63065397/156344382-821872f3-b6e3-46e7-b925-b5f1a0821da8.png")
            i = 1
            if number is None:
                number = 5
            for head in (data['data']['children']):
                embed.add_field(
                    name=str(i),
                    value=head['data']['title'][0:127] + "...",
                    inline=False
                )
                i += 1
                if i > number:
                    break
            if i <= number:
                embed.add_field(
                    name=str(i),
                    value="No more data could be received...",
                    inline=False
                )
            if number > 0:
                await ctx.send(reference=ctx.message, embed=embed)
            return
    # ----------------------------------------------------------------------------------------------------------------------

    async def get_crypto_rate(self, urlEnd):
        # ids=bitcoin&vs_currencies=inr
        API_URL = "https://api.coingecko.com/api/v3/simple/price?" + urlEnd
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as resp:
                quote_json = await resp.json(content_type=None)
                return (quote_json)

    @commands.command(name="crypto", aliases=["cryptocurrency", "crypto-price", "coingecko"], help="shows the price of given cryptocurrency(s) in given currency(s)")
    async def inspire_command(self, ctx, cryptocurrencies: str, currencies: Optional[str]):
        if currencies is None:
            currencies = "usd"
        cryptocurrencies = cryptocurrencies.lower()
        cryptocurrencies = cryptocurrencies.split(",")
        for i in range(len(cryptocurrencies)):
            cryptocurrencies[i] = cryptocurrencies[i].strip()
        cryptocurrencies = ",".join(cryptocurrencies)
        currencies = currencies.lower()
        currencies = currencies.split(",")
        for i in range(len(currencies)):
            currencies[i] = currencies[i].strip()
        currencies = ",".join(currencies)
        urlEnd = "ids="+cryptocurrencies+"&vs_currencies="+currencies
        rate = await self.get_crypto_rate(urlEnd)
        if (len(rate) == 0) or (len(rate[list(rate.keys())[0]]) == 0):
            async with ctx.typing():
                embed = discord.Embed(
                    title="",
                    description="",
                    color=0xff0000
                )
                embed.set_author(
                    name="Unknown error occured")
            await ctx.send(reference=ctx.message, embed=embed)
            return
        for cryptocurrency in rate.keys():
            async with ctx.typing():
                embed = discord.Embed(
                    title="",
                    description="",
                    color=0x00ff00
                )
                embed.set_author(
                    name=cryptocurrency.title()+" Price")
                for currency in rate[cryptocurrency].keys():
                    embed.add_field(
                        name=currency.upper(),
                        value=("{:,}".format(rate[cryptocurrency][currency])),
                        inline=True
                    )
            await ctx.send(reference=ctx.message, embed=embed)
        return

    # ----------------------------------------------------------------------------------------------------------------------
    @commands.command(name="tts", aliases=["text-to-speech"], help="converts given text to speech (english)")
    async def tts_command(self, ctx, *, text):
        if len(text) > 200:
            embed = discord.Embed(
                title="Error",
                description="Text too long",
                colour=0xff0000,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="given text: "+text)
            await ctx.send(reference=ctx.message, embed=embed)
            return
        if len(text) == 0:
            embed = discord.Embed(
                title="Error",
                description="Nothing to read",
                colour=0xff0000,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="given text: "+text)
            await ctx.send(reference=ctx.message, embed=embed)
            return
        tts = gTTS(text=text, lang='en')
        tts.save("tts.mp3")
        await ctx.send(file=discord.File("tts.mp3"))
        return

    # ----------------------------------------------------------------------------------------------------------------------
    async def get_qa(self):
        API_URL = "https://jservice.io/api/random"
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as resp:
                quote_json = await resp.json(content_type=None)
                return (quote_json)

    @commands.command(name="question", aliases=["q/a", "ask"], help="shows a random question and it's answer")
    async def question_command(self, ctx):
        random_qa = await self.get_qa()
        async with ctx.typing():
            embed = discord.Embed(
                title="Question",
                description=random_qa[0]['question'],
                color=0x00ff00
            )
            embed.add_field(
                name="Answer",
                value=random_qa[0]['answer'],
                inline=False
            )
            embed.add_field(
                name="Category",
                value=random_qa[0]['category']['title'],
                inline=True
            )
            embed.add_field(
                name="Difficulty",
                value=random_qa[0]['value'],
                inline=True
            )
        await ctx.send(reference=ctx.message, embed=embed)
        return

    # ----------------------------------------------------------------------------------------------------------------------


def setup(bot):
    bot.add_cog(Fun(bot))
