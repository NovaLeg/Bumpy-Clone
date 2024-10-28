import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='&', intents=intents)
bot.owner_ids = [1142754238179594240]

bot.remove_command('help')

async def load_cogs():
    await bot.load_extension('cogs.bump')
    await bot.load_extension('cogs.autobump')
    await bot.load_extension('cogs.info')
    await bot.load_extension('jishaku')

@bot.event
async def on_ready():
    print(f'Successfully {bot.user.name} has come online')
    await load_cogs()

@bot.check
def is_owner(ctx):
    return ctx.author.id in bot.owner_ids

if __name__ == "__main__":
    bot.run('')  
