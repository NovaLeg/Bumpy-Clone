import discord
from discord.ext import commands, tasks
import sqlite3
import time

class Bump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('bumps.db')
        self.link_db = sqlite3.connect('link.db')
        self.db.execute("CREATE TABLE IF NOT EXISTS bumps (guild_id INTEGER PRIMARY KEY, bumps INTEGER)")
        self.link_db.execute("CREATE TABLE IF NOT EXISTS links (guild_id INTEGER PRIMARY KEY, invite_link TEXT)")
        self.leaderboard_channel = None
        self.leaderboard_view = discord.ui.View()
        self.update_leaderboard.start()
        self.cooldowns = {}

    @commands.command(name='bump')
    async def bump(self, ctx):
        user_id = ctx.author.id
        current_time = time.time()

        if user_id in self.cooldowns:
            elapsed_time = current_time - self.cooldowns[user_id]
            if elapsed_time < 90:
                remaining_time = 90 - elapsed_time
                minutes, seconds = divmod(remaining_time, 60)
                msg = await ctx.send(f"You can use `&bump` after {int(minutes)} minute/s and {int(seconds)} second/s.")
                await msg.delete(delay=10)
                return

        guild_id = ctx.guild.id
        cur = self.db.cursor()
        cur.execute("INSERT OR IGNORE INTO bumps (guild_id, bumps) VALUES (?, 0)", (guild_id,))
        cur.execute("UPDATE bumps SET bumps = bumps + 1 WHERE guild_id = ?", (guild_id,))
        self.db.commit()
        total_bumps = cur.execute("SELECT bumps FROM bumps WHERE guild_id = ?", (guild_id,)).fetchone()[0]
        self.cooldowns[user_id] = current_time
        bump_msg = await ctx.send(embed=discord.Embed(description=f"Server bumped successfully!\nTotal Bumps of your server: {total_bumps}\nYou can bump again after {90} seconds.", color=0x474A69))
        await bump_msg.delete(delay=20)

    @commands.command(name='topbumps')
    async def topbumps(self, ctx, page: int = 1):
        user_id = ctx.author.id
        current_time = time.time()

        if user_id in self.cooldowns:
            elapsed_time = current_time - self.cooldowns[user_id]
            if elapsed_time < 90:
                remaining_time = 90 - elapsed_time
                minutes, seconds = divmod(remaining_time, 60)
                msg = await ctx.send(f"You can use `&topbumps` after {int(minutes)} minute(s) and {int(seconds)} second(s).")
                await msg.delete(delay=10)
                return

        cur = self.db.cursor()
        cur.execute("SELECT guild_id, bumps FROM bumps ORDER BY bumps DESC LIMIT 50")
        data = cur.fetchall()
        total_pages = (len(data) + 9) // 10
        start = (page - 1) * 10
        end = start + 10
        leaderboard = ""
        buttons = []

        for idx in range(start, min(end, len(data))):
            guild_id, bumps = data[idx]
            guild = self.bot.get_guild(guild_id)
            if guild:
                invite_link = await self.get_or_create_invite(guild)
                leaderboard += f"`[{idx + 1}]` [{guild.name}]({invite_link}): {bumps} bumps\n"
                buttons.append(discord.ui.Button(label=f"{idx + 1}", url=invite_link))

        embed = discord.Embed(title="Top 50 Servers with Most Bumps", description=leaderboard, color=0x474A69)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Page {page}/{total_pages}.")
        view = discord.ui.View()

        for button in buttons:
            view.add_item(button)

        if page > 1:
            view.add_item(discord.ui.Button(label="Previous", style=discord.ButtonStyle.secondary, custom_id="prev"))
        if page < total_pages:
            view.add_item(discord.ui.Button(label="Next", style=discord.ButtonStyle.secondary, custom_id="next"))

        await ctx.send(embed=embed, view=view)
        self.cooldowns[user_id] = current_time

    @commands.Cog.listener()
    async def on_button_click(self, interaction: discord.Interaction):
        if interaction.custom_id == "prev":
            page = int(interaction.message.embeds[0].footer.text.split('/')[0].split()[1]) - 1
            await self.topbumps(interaction.user, page)
            await interaction.response.defer()
        elif interaction.custom_id == "next":
            page = int(interaction.message.embeds[0].footer.text.split('/')[0].split()[1]) + 1
            await self.topbumps(interaction.user, page)
            await interaction.response.defer()

    @commands.command(name='setup')
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        guild = ctx.guild
        if not discord.utils.get(guild.text_channels, name="leaderboard"):
            self.leaderboard_channel = await guild.create_text_channel("leaderboard")
            await ctx.send(embed=discord.Embed(description="Leaderboard channel created successfully!\nTotal Bumps of your server: 0", color=0x474A69))
            if not self.update_leaderboard.is_running():
                self.update_leaderboard.start()

    async def get_or_create_invite(self, guild):
        cur = self.link_db.cursor()
        cur.execute("SELECT invite_link FROM links WHERE guild_id = ?", (guild.id,))
        row = cur.fetchone()
        if row:
            invite_link = row[0]
            try:
                invite = await self.bot.fetch_invite(invite_link)
                if invite.is_valid():
                    return invite_link
            except discord.NotFound:
                pass
        invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0)
        cur.execute("INSERT OR REPLACE INTO links (guild_id, invite_link) VALUES (?, ?)", (guild.id, invite.url))
        self.link_db.commit()
        return invite.url

    @tasks.loop(seconds=10)
    async def update_leaderboard(self):
        if self.leaderboard_channel is not None:
            cur = self.db.cursor()
            cur.execute("SELECT guild_id, bumps FROM bumps ORDER BY bumps DESC LIMIT 10")
            data = cur.fetchall()
            self.leaderboard_view.clear_items()
            leaderboard = ""

            for idx, (guild_id, bumps) in enumerate(data, 1):
                guild = self.bot.get_guild(guild_id)
                if guild:
                    leaderboard += f"`[{idx}]` {guild.name}: {bumps} bumps\n"
                    invite_link = await self.get_or_create_invite(guild)
                    button = discord.ui.Button(label=f"{idx}", url=invite_link)
                    self.leaderboard_view.add_item(button)

            embed = discord.Embed(title="Top Ten Active Servers", description=leaderboard, color=0x474A69)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.set_footer(text="List updates every 10 seconds.")
            await self.leaderboard_channel.send(embed=embed, view=self.leaderboard_view)

async def setup(bot):
    await bot.add_cog(Bump(bot))
