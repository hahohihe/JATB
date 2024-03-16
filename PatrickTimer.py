from discord.ext import commands
import asyncio
import datetime
import JATB
import PatrickCommand

SERVER_ID = 1202493390177050634
CHANNEL_ID = 1202493390177050637

async def PatrickTimer(bot: commands.Bot):
    chat_channel = bot.get_channel(CHANNEL_ID)
    
    while True :
        try :
            if JATB.isLoop :
                now = datetime.datetime.now()
                start_time = JATB.start_time
                end_time = JATB.end_time
                symbol = JATB.get_symbol()
                cur_price = JATB.get_current_price(symbol)
                
                if JATB.isAlarm :
                    if now.hour % JATB.alarm_period == 0 and now.minute == 0 and 0 < now.second < 5:
                        await SendMessage(chat_channel, 'System is running')
                        await asyncio.sleep(5)

                if now.hour == int(start_time[0:2]) and now.minute == int(start_time[2:4]) and 0 < now.second < 10:
                    JATB.get_best_k(JATB.get_symbol())
                    JATB.cal_target_price(symbol)
                    
                    long_target, short_target = JATB.long_target, JATB.short_target
                    open_price = JATB.get_open_price(JATB.get_symbol())

                    per_long = round((long_target / open_price - 1) * 100, 2)
                    per_short = round((short_target / open_price - 1) * 100, 2)

                    await SendMessage(chat_channel, 'Target position setting was successful')
                    await SendMessage(chat_channel, 'Long K = ' + str(JATB.longK) + ', Short K = ' + str(JATB.shortK))
                    await SendMessage(chat_channel, 'Long Target = ' + str(long_target) + ' ({0:>+}'.format(per_long) + '%)')
                    await SendMessage(chat_channel, 'Short Target = ' + str(short_target) + ' ({0:>+}'.format(per_short) + '%)')
                    await asyncio.sleep(10)
                
                if now.hour == int(end_time[0:2]) and now.minute == int(end_time[2:4]) and 0 < now.second < 10:
                    JATB.exit_position(symbol)
                    JATB.isTarget = False
                    await SendMessage(chat_channel, 'Position closed due to market close')
                    await asyncio.sleep(10)

                if JATB.isTarget:
                    if JATB.position['Type'] == 'None' :
                        if cur_price > JATB.long_target :
                            amount = JATB.get_amount(symbol, cur_price)
                            JATB.enter_position('Long', symbol, cur_price, amount)
                            await SendMessage(chat_channel, 'Successful entry into Long Position')
                        elif cur_price < JATB.short_target :
                            amount = JATB.get_amount(symbol, cur_price)
                            JATB.enter_position('Short', symbol, cur_price, amount)
                            await SendMessage(chat_channel, 'Successful entry into Short Position')
                    # elif JATB.position['Type'] == 'Long' :
                    #     if cur_price < JATB.short_target :
                    #         JATB.exit_position(symbol)
                    #         await SendMessage(chat_channel, 'Chnage position from Long to Short')
                    # elif JATB.position['Type'] == 'Short' :
                    #     if cur_price > JATB.long_target :
                    #         JATB.exit_position(symbol)
                    #         await SendMessage(chat_channel, 'Chnage position from Short to Long')
        except Exception as e:
           await SendMessage(chat_channel, '[Error]' + str(e))
           await asyncio.sleep(10)
        await asyncio.sleep(1)
            
async def SendMessage(channel, msg):
    await channel.send(msg)