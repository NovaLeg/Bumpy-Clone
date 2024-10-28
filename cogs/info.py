import discord
from discord.ext import commands
import time

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(name='help')
    @commands.cooldown(1, 90, commands.BucketType.user)
    async def help(self, ctx):
        embed = discord.Embed(color=0x474A69)
        embed.title = "Hi, I'm Bumpy!"
        embed.description = (
            "I'm here to help promote your server with just a simple bump. Want to grow your community and increase your visibility? Just bump with us once, and I'll place your server in front of thousands of users, ready for discovery! With my help, you can bring in fresh faces, new conversations, and foster an active, thriving community. Let's bump your server to the top and watch it grow!"
        )
        embed.add_field(name="My Prefix", value="`&` | Type `&setup` to startup.")
        embed.add_field(name="Commands", value="`&setup` - Sets up the Bump Master in your server.\n"
                                                "`&bump` - Boosts your server instantly!\n"
                                                "`&topbumps` - Displays the top 50 servers with the most bumps.\n"
                                                "`&autobump` - Gives you one bump for every 5m.")
        embed.set_footer(text="Join the support server for premium access and help.")
        await ctx.send(embed=embed)

    @commands.command(name='stats')
    @commands.cooldown(1, 90, commands.BucketType.user)
    async def stats(self, ctx):
        current_time = time.time()
        uptime_seconds = current_time - self.start_time
        uptime_days, uptime_seconds = divmod(uptime_seconds, 86400)
        uptime_hours, uptime_seconds = divmod(uptime_seconds, 3600)
        uptime_minutes, uptime_seconds = divmod(uptime_seconds, 60)

        embed = discord.Embed(color=0x474A69)
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
        embed.title = "**__Bot Information__**"
        embed.description = f"""```ahk
Guilds: {len(self.bot.guilds)}
Users: {len(self.bot.users)}
Latency: {round(self.bot.latency * 1000)} MS
Online Since: {int(uptime_days)} day(s), {int(uptime_hours)} hour(s), {int(uptime_minutes)} minute(s) and {int(uptime_seconds)} second(s)
```"""
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
