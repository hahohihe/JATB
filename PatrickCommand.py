import discord
from discord.ext import commands
import JATB

version = '2.1'

class PatrickCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='init')
    async def init_group(self, ctx: discord.ext.commands.Context):
        JATB.init()
        await ctx.send('Succesful initialize, Please start loop again')

    @commands.group(name='ver')
    async def init_group(self, ctx: discord.ext.commands.Context):
        await ctx.send(version)

    @commands.group(name='show')
    async def show_group(self, ctx: discord.ext.commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Command is incorrect')
    
    @show_group.command(name='symbol')
    async def show_symbol(self, ctx: discord.ext.commands.Context):
        await ctx.send('Current symbol = ' + JATB.get_symbol())

    @show_group.command(name='price')
    async def show_price(self, ctx: discord.ext.commands.Context):
        cur_price = JATB.get_current_price(JATB.get_symbol())
        open_price = JATB.get_open_price(JATB.get_symbol())
        per = round((cur_price / open_price) - 1, 2)
        await ctx.send('Current Price = ' + str(cur_price) + ' ({0:>+}'.format(per) + '%)')

    @show_group.command(name='target')
    async def show_target(self, ctx: discord.ext.commands.Context):
        if JATB.isTarget == False :
            await ctx.send('Target is not set')
        else :
            cur_price = JATB.get_current_price(JATB.get_symbol())
            open_price = JATB.get_open_price(JATB.get_symbol())
            per = round((cur_price / open_price - 1) * 100, 2)

            long_target, short_target = JATB.long_target, JATB.short_target
            per_long = round((long_target / open_price - 1) * 100, 2)
            per_short = round((short_target / open_price - 1) * 100, 2)

            await ctx.send('Long K = ' + str(JATB.longK) + ', Short K = ' + str(JATB.shortK))
            await ctx.send('Current Price = ' + str(cur_price) + ' ({0:>+}'.format(per) + '%)')
            await ctx.send('Long Target = ' + str(long_target) + ' ({0:>+}'.format(per_long) + '%)')
            await ctx.send('Short Target = ' + str(short_target) + ' ({0:>+}'.format(per_short) + '%)')

    @show_group.command(name='position')
    async def show_position(self, ctx: discord.ext.commands.Context):
        cur_price = JATB.get_current_price(JATB.get_symbol())
        position = JATB.get_position()
        if position['Type'] == 'None' :
            await ctx.send('The position has not been entered') 
        else :
            roi = round((cur_price / position['EntryPrice'] - 1) * 100, 2)
            pnl = round((cur_price / position['EntryPrice'] - 1) * position['Size'], 2)
            await ctx.send('Type = ' + position['Type'])
            await ctx.send('EntryPrice = ' + str(position['EntryPrice']))
            await ctx.send('Amount = ' + str(position['Amount']))
            await ctx.send('Size = ' + str(position['Size']))
            await ctx.send('ROI = ' + '{0:>+}'.format(roi) + '%')
            await ctx.send('PNL = ' + '{0:>+}'.format(pnl) + ' USDT')

    @show_group.command(name='alarm')
    async def show_alarm(self, ctx: discord.ext.commands.Context):
        await ctx.send('Alarm Setting = ' + str(JATB.alarm_period) + '(hour)')

    @show_group.command(name='time')
    async def show_time(self, ctx: discord.ext.commands.Context, text):
        if text == 'start' :
            await ctx.send('Start time = ' + JATB.start_time[0:2] + ':' + JATB.start_time[2:4])
        elif text =='end' :
            await ctx.send('End time = ' + JATB.end_time[0:2] + ':' + JATB.end_time[2:4])

    @commands.group(name='set')
    async def set_group(self, ctx: discord.ext.commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Command is incorrect')
            
    @set_group.command(name='target')
    async def set_target(self, ctx: discord.ext.commands.Context):
        JATB.get_best_k(JATB.get_symbol())
        JATB.cal_target_price(JATB.get_symbol())

        long_target, short_target = JATB.long_target, JATB.short_target
        open_price = JATB.get_open_price(JATB.get_symbol())

        per_long = round((long_target / open_price - 1) * 100, 2)
        per_short = round((short_target / open_price - 1) * 100, 2)

        await ctx.send('Target position setting was successful')
        await ctx.send('Long K = ' + str(JATB.longK) + ', Short K = ' + str(JATB.shortK))
        await ctx.send('Long Target = ' + str(long_target) + ' ({0:>+}'.format(per_long) + '%)')
        await ctx.send('Short Target = ' + str(short_target) + ' ({0:>+}'.format(per_short) + '%)')

    @set_group.command(name='alarm')
    async def set_alarm(self, ctx: discord.ext.commands.Context, value):
        JATB.alarm_period = int(value)
        await ctx.send('Alarm setting successful')
        await ctx.send('Alarm Setting = ' + str(JATB.alarm_period) + '(hour)')

    @set_group.command(name='time')
    async def set_time(self, ctx: discord.ext.commands.Context, text, value):
        if text == 'start' :
            JATB.start_time = value
            await ctx.send('Successfully set new start time')
            await ctx.send('Start time = ' + JATB.start_time[0:2] + ':' + JATB.start_time[2:4])
        elif text == 'end' : 
            JATB.end_time = value
            await ctx.send('Successfully set new end time') 
            await ctx.send('End time = ' + JATB.end_time[0:2] + ':' + JATB.end_time[2:4])

    @commands.group(name='start')
    async def start_group(self, ctx: discord.ext.commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Command is incorrect')

    @start_group.command(name='loop')
    async def start_loop(self, ctx: discord.ext.commands.Context):
        JATB.isLoop = True
        await ctx.send('Loop on')

    @start_group.command(name='alarm')
    async def start_alarm(self, ctx: discord.ext.commands.Context):
        JATB.isAlarm = True
        await ctx.send('Alarm on')

    @commands.group(name='stop')
    async def stop_group(self, ctx: discord.ext.commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('Command is incorrect')

    @stop_group.command(name='loop')
    async def stop_loop(self, ctx: discord.ext.commands.Context):
        JATB.isLoop = False
        await ctx.send('Loop off')

    @stop_group.command(name='alarm')
    async def stop_alarm(self, ctx: discord.ext.commands.Context):
        JATB.isAlarm = False
        await ctx.send('Alarm is off')