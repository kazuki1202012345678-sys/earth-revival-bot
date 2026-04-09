import os
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import asyncio
from datetime import datetime

# Import modules
from modules.cn_monitor import check_chinese_sns
from modules.yt_monitor import check_youtube
from modules.pve_monitor import check_pve_strategy

# Load environment variables
load_dotenv()

# --- Keep-alive Server (Flask) ---
# for Render.com 24h keeping
app = Flask('')

@app.route('/')
def home():
            return {"status": "ok", "message": "Earth Revival Bot (Pimport os
            import discord
            from discord.ext import tasks, commands
        from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import asyncio
from datetime import datetime

# Import modules
from modules.cn_monitor import check_chinese_sns
from modules.yt_monitor import check_youtube
from modules.pve_monitor import check_pve_strategy

# Load environment variables
load_dotenv()

# --- Keep-alive Server (Flask) ---
# for Render.com 24h keeping
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
        
# --- Discord Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
            print(f'[SYSTEM] Logged in as {bot.user.name} (ID: {bot.user.id})')
            # Start periodic jobs
    if not update_jobs.is_running():
                    update_jobs.start()
            
@tasks.loop(hours=1)
async def update_jobs():
            now = datetime.now()
            print(f'[CRON] Periodic task execution: {now.strftime("%Y-%m-%d %H:%M:%S")}')
            
            # Check YouTube
    await check_youtube(bot)
    
    # Daily update at 8:00 AM JST
    if now.hour == 8:
                    print('[CRON] Running morning updates (SNS & PvE)...')
                    await check_chinese_sns(bot)
                    await check_pve_strategy(bot)
            
@bot.command()
async def update(ctx):
            """Manual update command"""
            if not ctx.author.guild_permissions.administrator:
                            return await ctx.send("Admin only.")
                        
            await ctx.send("Checking latest info...")
            await check_youtube(bot)
            await check_chinese_sns(bot, force=True)
            await ctx.send("Check complete.")
        
if __name__ == "__main__":
            # Start keep-alive server
            keep_alive()
            
            # Start Discord Bot
    token = os.getenv('DISCORD_TOKEN')
    if token:
                    try:
                                        bot.run(token)
                    except Exception as e:
                                        print(f'[ERROR] Failed to start bot: {e}')
                    else:
                                    print('[ERROR] DISCORD_TOKEN not found')
                            thon) is running"}

def run_flask():
            port = int(os.getenv('PORT', 3000))
            app.run(host='0.0.0.0', port=port)

def keep_alive():
            t = Thread(target=run_flask)
            t.start()

# --- Discord Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
            print(f'[SYSTEM] Logged in as {bot.user.name} (ID: {bot.user.id})')
            # Start periodic jobs
            if not update_jobs.is_running():
                            update_jobs.start()

        @tasks.loop(hours=1)
async def update_jobs():
            now = datetime.now()
            print(f'[CRON] Periodic task execution: {now.strftime("%Y-%m-%d %H:%M:%S")}')

    # Check YouTube
            await check_youtube(bot)

    # Daily update at 8:00 AM JST
            if now.hour == 8:
                            print('[CRON] Running morning updates (SNS & PvE)...')
                            await check_chinese_sns(bot)
                            await check_pve_strategy(bot)

        @bot.command()
async def update(ctx):
            """Manual update command"""
            if not ctx.author.guild_permissions.administrator:
                            return await ctx.send("Admin only.")

            await ctx.send("Checking latest info...")
            await check_youtube(bot)
            await check_chinese_sns(bot, force=True)
            await ctx.send("Check complete.")

if __name__ == "__main__":
            # Start keep-alive server
            keep_alive()

    # Start Discord Bot
            token = os.getenv('DISCORD_TOKEN')
            if token:
                            try:
                                                bot.run(token)
except Exception as e:
            print(f'[ERROR] Failed to start bot: {e}')
else:
        print('[ERROR] DISCORD_TOKEN not found')
        
