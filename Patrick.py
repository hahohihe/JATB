import discord
from discord.ext import commands
from PatrickCommand import PatrickCommand
from PatrickTimer import PatrickTimer

def GetToken() :
    f = open('token.txt')
    token = f.readline()
    f.close()
    return token

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='@', intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.add_cog(PatrickCommand(bot))
    await bot.loop.create_task(PatrickTimer(bot))
                         
bot.run(GetToken())