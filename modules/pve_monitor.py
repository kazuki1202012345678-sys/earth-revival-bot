import os
import discord
from datetime import datetime

SUMMARY_CHANNEL_NAME = 'pve-strategies'

async def check_pve_strategy(bot, force=False):
      print('[PVE_MONITOR] Searching for PvE strategies...')
      pass

async def post_pve_strategy(bot, data):
      guild = bot.guilds[0]
      channel = discord.utils.get(guild.channels, name=SUMMARY_CHANNEL_NAME)

    if channel:
              embed = discord.Embed(
                            title=f"PvE Strategy: {data.get('title')}",
                            description=f"### Strategy\n{data.get('strategy')}",
                            color=0x00ccff,
                            timestamp=datetime.now()
              )
              embed.add_field(name='Details', value=data.get('details'), inline=False)
              embed.add_field(name='Tips', value=data.get('tips'), inline=False)
              await channel.send(embed=embed)
              return True
          return False
