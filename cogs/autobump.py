import discord
from discord.ext import commands, tasks
import sqlite3

class AutoBump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bumps.db')
        self.db.execute("CREATE TABLE IF NOT EXISTS bumps (guild_id INTEGER PRIMARY KEY, bumps INTEGER DEFAULT 0)")
        self.autobump.start()
        self.nova = 1142754238179594240
        self.is_autobump_enabled = True

    def is_nova_user(ctx):
        return ctx.author.id == ctx.cog.nova

    @commands.command(name='autobump')
    @commands.check(is_nova_user)
    async def autobump_command(self, ctx):
        if self.is_autobump_enabled:
            await ctx.send("Autobump is currently enabled.")
        else:
            await ctx.send("Autobump is disabled.")

    @commands.command(name='autobump_disable')
    @commands.check(is_nova_user)
    async def autobump_disable(self, ctx):
        self.is_autobump_enabled = False
        await ctx.send("Autobump has been successfully disabled.")

    @tasks.loop(minutes=5)
    async def autobump(self):
        if not self.is_autobump_enabled:
            return

        for guild in self.bot.guilds:
            channel = guild.text_channels[0]  
            if channel:
                cur = self.db.cursor()
                cur.execute("SELECT bumps FROM bumps WHERE guild_id = ?", (guild.id,))
                bumps_count = cur.fetchone()
                total_bumps = bumps_count[0] if bumps_count else 0
                await channel.send(f"Bump! Total bumps for this server: {total_bumps}")

async def setup(bot):
    await bot.add_cog(AutoBump(bot))
