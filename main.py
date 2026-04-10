import os
import json
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import asyncio
from datetime import datetime

from modules.cn_monitor import check_chinese_sns
from modules.yt_monitor import check_youtube
from modules.pve_monitor import check_pve_strategy

load_dotenv()
app = Flask('')

@app.route('/')
def home():
              return {"status": "ok", "message": "Earth Revival Bot (Python) is running"}

def run_flask():
              port = int(os.getenv('PORT', 3000))
              app.run(host='0.0.0.0', port=port)

def keep_alive():
              t = Thread(target=run_flask)
              t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

STATE_PATH = os.path.join(os.path.dirname(__file__), 'data/cron_state.json')

def get_jst_now():
              return datetime.fromtimestamp(datetime.now().timestamp() + 9*3600)

def should_run_morning_update():
              now = get_jst_now()
              last_run_date = ""
              if os.path.exists(STATE_PATH):
                                try:
                                                      with open(STATE_PATH, 'r') as f:
                                                                                state = json.load(f)
                                                                                last_run_date = state.get('last_morning_run', "")
                                                                        except:
                                                      pass
                            current_date = now.strftime('%Y-%m-%d')
    if last_run_date != current_date and now.hour >= 8:
                      return True
                  return False

def mark_morning_update_done():
              now = get_jst_now()
    state = {}
    if os.path.exists(STATE_PATH):
                      try:
                                            with open(STATE_PATH, 'r') as f:
                                                                      state = json.load(f)
                                                              except:
                                            pass
                  state['last_morning_run'] = now.strftime('%Y-%m-%d')
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, 'w') as f:
                      json.dump(state, f)

@bot.event
async def on_ready():
              print(f'[SYSTEM] Logged in as {bot.user.name}')
    if not update_jobs.is_running():
                      update_jobs.start()

@tasks.loop(minutes=30)
async def update_jobs():
              try:
                                await check_youtube(bot)
except Exception as e:
        print(f'[ERROR] YouTube check failed: {e}')
    if should_run_morning_update():
                      print('[CRON] Starting morning updates...')
        try:
                              await check_chinese_sns(bot)
                              await check_pve_strategy(bot)
                              mark_morning_update_done()
except Exception as e:
            print(f'[ERROR] Morning updates failed: {e}')

@bot.command()
async def update(ctx):
              if not ctx.author.guild_permissions.administrator:
                                return await ctx.send("Administrator permission required.")
                            await ctx.send("Checking for updates...")
    await check_youtube(bot)
    await check_chinese_sns(bot, force=True)
    await ctx.send("Done.")

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
                      bot.run(token)
